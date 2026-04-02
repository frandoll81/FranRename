const { invoke, convertFileSrc } = window.__TAURI__.core;
const { listen } = window.__TAURI__.event;
const { getCurrentWindow } = window.__TAURI__.window;

const appWindow = getCurrentWindow();

let files = [];
let currentFileIndex = -1;
let isSelecting = false;
let startX, startY, endX, endY;

// UI Elements
const dropZone = document.getElementById('drop-zone');
const fileList = document.getElementById('file-list');
const canvas = document.getElementById('crop-canvas');
const ctx = canvas.getContext('2d');
const container = document.getElementById('canvas-container');
const dropMsg = document.getElementById('drop-msg');
const statusText = document.getElementById('status-text');
const fileCountBadge = document.getElementById('file-count');

// Titlebar Controls
document.getElementById('titlebar-minimize').onclick = () => appWindow.minimize();
document.getElementById('titlebar-maximize').onclick = () => appWindow.toggleMaximize();
document.getElementById('titlebar-close').onclick = () => appWindow.close();

// Listen for file drops
listen('tauri://drag-drop', (event) => {
  const paths = event.payload.paths;
  addFiles(paths);
});

function addFiles(paths) {
  paths.forEach(path => {
    if (!files.find(f => f.path === path)) {
      files.push({
        path,
        name: path.split(/[/\\]/).pop(),
        newName: '',
        processed: false
      });
    }
  });
  updateUI();
}

function updateUI() {
  fileCountBadge.innerText = `${files.length} files`;
  renderFileList();
}

function renderFileList() {
  if (files.length === 0) {
    fileList.innerHTML = '<div class="empty-state"><p>Drop images to start</p></div>';
    return;
  }

  fileList.innerHTML = files.map((file, index) => `
    <div class="file-item ${index === currentFileIndex ? 'active' : ''}" onclick="selectFile(${index})">
      <div style="font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 13px;">${file.name}</div>
      <div style="font-size: 11px; color: ${file.newName ? 'var(--accent-color)' : 'var(--text-secondary)'}; margin-top: 4px;">
        ${file.newName || 'Waiting for OCR...'}
      </div>
    </div>
  `).join('');
}

window.selectFile = (index) => {
  currentFileIndex = index;
  renderFileList();
  loadImage(files[index].path);
};

function loadImage(path) {
  const assetUrl = convertFileSrc(path);
  const img = new Image();
  img.onload = () => {
    dropMsg.style.display = 'none';
    container.style.display = 'flex';
    // Calculate aspect ratio fit
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);
    statusText.innerText = `Selected: ${files[currentFileIndex].name}`;
  };
  img.src = assetUrl;
}

// Canvas Selection
canvas.addEventListener('mousedown', (e) => {
  if (currentFileIndex === -1) return;
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  startX = (e.clientX - rect.left) * scaleX;
  startY = (e.clientY - rect.top) * scaleY;
  isSelecting = true;
});

canvas.addEventListener('mousemove', (e) => {
  if (!isSelecting) return;
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  endX = (e.clientX - rect.left) * scaleX;
  endY = (e.clientY - rect.top) * scaleY;
  drawSelection();
});

canvas.addEventListener('mouseup', async () => {
  if (!isSelecting) return;
  isSelecting = false;
  if (Math.abs(endX - startX) > 5 && Math.abs(endY - startY) > 5) {
    const coords = [
      Math.min(startX, endX),
      Math.min(startY, endY),
      Math.abs(endX - startX),
      Math.abs(endY - startY)
    ].map(Math.round);
    
    await performOCR(coords);
  }
});

function drawSelection() {
  const assetUrl = convertFileSrc(files[currentFileIndex].path);
  const img = new Image();
  img.onload = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0);
    
    ctx.fillStyle = 'rgba(0,0,0,0.4)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    const x = Math.min(startX, endX);
    const y = Math.min(startY, endY);
    const w = Math.abs(endX - startX);
    const h = Math.abs(endY - startY);
    
    ctx.clearRect(x, y, w, h);
    ctx.drawImage(img, x, y, w, h, x, y, w, h);
    
    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 4;
    ctx.strokeRect(x, y, w, h);
  };
  img.src = assetUrl;
}

async function performOCR(coords) {
  statusText.innerText = 'Recognizing text...';
  try {
    const result = await invoke('run_ocr', { 
      imagePath: files[currentFileIndex].path, 
      coords: coords.join(',') 
    });
    
    const data = JSON.parse(result);
    if (data.text) {
      const ext = files[currentFileIndex].path.substring(files[currentFileIndex].path.lastIndexOf('.'));
      files[currentFileIndex].newName = data.text + ext;
      renderFileList();
      statusText.innerText = `Recognized: "${data.text}"`;
    } else {
      statusText.innerText = `Error: ${data.error || 'Empty result'}`;
    }
  } catch (err) {
    console.error(err);
    statusText.innerText = 'Detection failed';
  }
}

document.getElementById('process-btn').onclick = async () => {
  let count = 0;
  statusText.innerText = 'Processing renaming...';
  for (let file of files) {
    if (file.newName && file.newName !== file.name) {
      try {
        await invoke('rename_file', { oldPath: file.path, newName: file.newName });
        count++;
      } catch (e) {
        console.error(e);
      }
    }
  }
  statusText.innerText = `Successfully renamed ${count} files!`;
  files = [];
  currentFileIndex = -1;
  updateUI();
  container.style.display = 'none';
  dropMsg.style.display = 'flex';
};

document.getElementById('clear-btn').onclick = () => {
  files = [];
  currentFileIndex = -1;
  updateUI();
  container.style.display = 'none';
  dropMsg.style.display = 'flex';
  statusText.innerText = 'Ready';
};
