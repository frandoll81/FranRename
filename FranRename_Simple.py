import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import easyocr
import os
import shutil

class FranRenameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FranRename - Simple OCR Renamer")
        self.root.geometry("1000x800")
        
        # OCR 엔진 초기화 (최초 실행 시 다소 걸릴 수 있음)
        self.reader = easyocr.Reader(['ko', 'en'])
        
        # 상태 변수
        self.image_path = None
        self.image = None
        self.display_img = None
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.roi = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # 상단 버튼 센터
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="사진 불러오기", command=self.load_image, bg="#2196F3", fg="white", padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="전체 초기화", command=self.reset, bg="#f44336", fg="white", padx=10).pack(side=tk.LEFT, padx=5)
        
        # 캔버스 (이미지 표시 및 드래그)
        self.canvas = tk.Canvas(self.root, cursor="cross", bg="#eee")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # 하단 결과 센터
        res_frame = tk.Frame(self.root)
        res_frame.pack(pady=10, fill=tk.X, padx=20)
        
        tk.Label(res_frame, text="인식된 텍스트:").pack(side=tk.LEFT)
        self.text_entry = tk.Entry(res_frame, width=50)
        self.text_entry.pack(side=tk.LEFT, padx=10)
        
        tk.Button(res_frame, text="파일명 변경하기", command=self.rename_file, bg="#4CAF50", fg="white", padx=20).pack(side=tk.LEFT)

        # 드래그 이벤트 바인딩
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if not file_path: return
        
        self.image_path = file_path
        self.image = Image.open(file_path)
        
        # 캔버스 크기에 맞게 리사이징 (비율 유지)
        w, h = self.image.size
        ratio = min(960/w, 600/h)
        new_w, new_h = int(w*ratio), int(h*ratio)
        
        self.resized_img = self.image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.display_img = ImageTk.PhotoImage(self.resized_img)
        self.ratio = ratio # 저장해두기
        
        self.canvas.config(width=new_w, height=new_h)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.display_img)
        self.reset_rect()

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect: self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline="red", width=2)

    def on_move_press(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        end_x, end_y = (event.x, event.y)
        self.perform_ocr(self.start_x, self.start_y, end_x, end_y)

    def perform_ocr(self, x1, y1, x2, y2):
        if not self.image: return
        
        # 캔버스 좌표를 원본 이미지 좌표로 변환
        ix1, iy1 = int(min(x1, x2) / self.ratio), int(min(y1, y2) / self.ratio)
        ix2, iy2 = int(max(x1, x2) / self.ratio), int(max(y1, y2) / self.ratio)
        
        cropped = self.image.crop((ix1, iy1, ix2, iy2))
        
        # OCR 수행
        results = self.reader.readtext(cropped)
        result_text = " ".join([res[1] for res in results])
        
        self.text_entry.delete(0, tk.END)
        self.text_entry.insert(0, result_text.strip())

    def rename_file(self):
        new_name = self.text_entry.get().strip()
        if not self.image_path or not new_name:
            messagebox.showwarning("주의", "사진을 불러오고 영역을 선택해 주세요!")
            return
            
        dir_path = os.path.dirname(self.image_path)
        ext = os.path.splitext(self.image_path)[1]
        
        # 특수문자 제거 (파일명 안전용)
        safe_name = "".join([c for c in new_name if c.isalnum() or c in (' ', '-', '_')]).strip()
        new_file_path = os.path.join(dir_path, f"{safe_name}{ext}")
        
        try:
            shutil.move(self.image_path, new_file_path)
            messagebox.showinfo("성공", f"파일명이 성공적으로 변경되었습니다!\n-> {safe_name}{ext}")
            self.reset()
        except Exception as e:
            messagebox.showerror("에러", f"파일명 변경 중 오류 발생: {e}")

    def reset_rect(self):
        if self.rect: self.canvas.delete(self.rect)
        self.rect = None

    def reset(self):
        self.canvas.delete("all")
        self.text_entry.delete(0, tk.END)
        self.image_path = None
        self.image = None

if __name__ == "__main__":
    root = tk.Tk()
    app = FranRenameApp(root)
    root.mainloop()
