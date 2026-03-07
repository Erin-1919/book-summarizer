// --- Globals (set from inline script in index.html) ---
// booksData, selectedBook, selectedChapter, selectedSubchapter

function getCurrentBook() {
  return booksData.find(b => b.id === selectedBook);
}

// --- Subchapter dropdown ---
function updateSubchapterSelect() {
  const sel = document.getElementById('chapterSelect');
  const subSel = document.getElementById('subchapterSelect');
  subSel.innerHTML = '<option value="">Select sub-chapter...</option>';
  const book = getCurrentBook();
  if (!book) return;
  const ch = book.chapters.find(c => c.id === sel.value);
  if (ch) {
    ch.subchapters.forEach(sc => {
      const opt = document.createElement('option');
      opt.value = sc.id;
      opt.textContent = sc.name;
      if (sc.id === selectedSubchapter) opt.selected = true;
      subSel.appendChild(opt);
    });
  }
}

function switchBook(bookId) {
  window.location.href = '/?book=' + encodeURIComponent(bookId);
}

// --- Chapter tree toggle ---
function toggleChapter(el) {
  const arrow = el.querySelector('.arrow');
  const list = el.nextElementSibling;
  if (list.style.display === 'none') {
    list.style.display = '';
    arrow.classList.add('open');
  } else {
    list.style.display = 'none';
    arrow.classList.remove('open');
  }
}

// --- Modals ---
function openBookModal() {
  document.getElementById('bookModal').classList.add('show');
  document.getElementById('bookTitleInput').focus();
}
function openChapterModal() {
  document.getElementById('chapterModal').classList.add('show');
  document.getElementById('chapterNameInput').focus();
}
function openSubchapterModal(chapterId) {
  document.getElementById('subchapterParentId').value = chapterId;
  document.getElementById('subchapterModal').classList.add('show');
  document.getElementById('subchapterNameInput').focus();
}
function closeModals() {
  document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('show'));
}

async function createBook() {
  const title = document.getElementById('bookTitleInput').value.trim();
  const authors = document.getElementById('bookAuthorsInput').value.trim();
  if (!title) return;
  const res = await fetch('/book', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({title, authors})
  });
  if (res.ok) {
    const data = await res.json();
    window.location.href = '/?book=' + encodeURIComponent(data.book.id);
  }
}

async function createChapter() {
  const name = document.getElementById('chapterNameInput').value.trim();
  if (!name) return;
  const res = await fetch('/chapter', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({book_id: selectedBook, name})
  });
  if (res.ok) location.reload();
}

async function createSubchapter() {
  const name = document.getElementById('subchapterNameInput').value.trim();
  const chapter_id = document.getElementById('subchapterParentId').value;
  if (!name) return;
  const res = await fetch('/subchapter', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({book_id: selectedBook, chapter_id, name})
  });
  if (res.ok) location.reload();
}

// --- Upload - Step 1: upload files, show order confirmation ---
let pendingFiles = [];

document.getElementById('uploadForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  const form = new FormData(this);
  const btn = document.getElementById('submitBtn');
  const status = document.getElementById('statusMsg');

  btn.disabled = true;
  status.className = 'status-msg';
  status.innerHTML = '<span class="spinner"></span> Uploading files...';

  try {
    const res = await fetch('/upload', { method: 'POST', body: form });
    const data = await res.json();
    if (!res.ok) {
      status.className = 'status-msg error';
      status.textContent = data.error || 'Something went wrong.';
      btn.disabled = false;
      return;
    }
    pendingFiles = data.files;
    status.textContent = '';
    showFileOrderPanel();
  } catch (err) {
    status.className = 'status-msg error';
    status.textContent = 'Network error. Please try again.';
    btn.disabled = false;
  }
});

function showFileOrderPanel() {
  const panel = document.getElementById('fileOrderPanel');
  const list = document.getElementById('fileOrderList');
  list.innerHTML = '';
  pendingFiles.forEach((f, i) => {
    const li = document.createElement('li');
    li.className = 'file-order-item';
    li.draggable = true;
    li.dataset.id = f.id;
    li.innerHTML = `<span class="grip">&#9776;</span><span class="file-num">${i + 1}.</span><span>${escapeHtml(f.name)}</span>`;
    list.appendChild(li);
  });
  panel.classList.add('show');
  document.getElementById('processStatusMsg').textContent = '';
  initDragAndDrop();
}

// --- Drag and drop ---
function initDragAndDrop() {
  const list = document.getElementById('fileOrderList');
  let dragItem = null;

  list.addEventListener('dragstart', e => {
    dragItem = e.target.closest('.file-order-item');
    if (dragItem) dragItem.classList.add('dragging');
  });
  list.addEventListener('dragend', e => {
    if (dragItem) dragItem.classList.remove('dragging');
    dragItem = null;
    updateNumbers();
  });
  list.addEventListener('dragover', e => {
    e.preventDefault();
    const afterEl = getDragAfterElement(list, e.clientY);
    if (afterEl == null) {
      list.appendChild(dragItem);
    } else {
      list.insertBefore(dragItem, afterEl);
    }
  });
}

function getDragAfterElement(container, y) {
  const items = [...container.querySelectorAll('.file-order-item:not(.dragging)')];
  return items.reduce((closest, child) => {
    const box = child.getBoundingClientRect();
    const offset = y - box.top - box.height / 2;
    if (offset < 0 && offset > closest.offset) {
      return { offset, element: child };
    }
    return closest;
  }, { offset: Number.NEGATIVE_INFINITY }).element;
}

function updateNumbers() {
  const items = document.querySelectorAll('#fileOrderList .file-order-item');
  items.forEach((item, i) => {
    item.querySelector('.file-num').textContent = (i + 1) + '.';
  });
}

function cancelOrder() {
  document.getElementById('fileOrderPanel').classList.remove('show');
  document.getElementById('submitBtn').disabled = false;
  pendingFiles = [];
}

// --- Step 2: process in confirmed order ---
async function confirmAndProcess() {
  const items = document.querySelectorAll('#fileOrderList .file-order-item');
  const orderedIds = [...items].map(li => li.dataset.id);
  const btn = document.getElementById('confirmOrderBtn');
  const status = document.getElementById('processStatusMsg');

  btn.disabled = true;
  status.className = 'status-msg';
  status.innerHTML = '<span class="spinner"></span> Extracting text & generating summary...';

  try {
    const res = await fetch('/process', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        file_ids: orderedIds,
        book_id: document.getElementById('bookIdInput').value,
        chapter_id: document.getElementById('chapterSelect').value,
        subchapter_id: document.getElementById('subchapterSelect').value,
      })
    });
    const data = await res.json();
    if (!res.ok) {
      status.className = 'status-msg error';
      status.textContent = data.error || 'Something went wrong.';
      btn.disabled = false;
      return;
    }
    status.textContent = 'Done!';
    document.getElementById('fileOrderPanel').classList.remove('show');
    document.getElementById('submitBtn').disabled = false;
    pendingFiles = [];
    const result = document.getElementById('uploadResult');
    result.innerHTML = `
      <div class="summary-card">
        <div class="timestamp">${data.entry.timestamp.slice(0,16).replace('T',' ')}</div>
        <button class="toggle-extracted" onclick="toggleExtracted(this)">Show extracted text</button>
        <div class="extracted" style="display:none">${escapeHtml(data.entry.extracted_text)}</div>
        <h4>Summary</h4>
        <div class="text-block">${escapeHtml(data.entry.summary)}</div>
      </div>`;
  } catch (err) {
    status.className = 'status-msg error';
    status.textContent = 'Network error. Please try again.';
    btn.disabled = false;
  }
}

// --- Delete summary ---
async function deleteSummary(id) {
  if (!confirm('Delete this summary?')) return;
  const res = await fetch(`/summary/${id}`, { method: 'DELETE' });
  if (res.ok) {
    const card = document.getElementById('card-' + id);
    if (card) card.remove();
  }
}

// --- Toggle extracted text ---
function toggleExtracted(btn) {
  const div = btn.nextElementSibling;
  if (div.style.display === 'none') {
    div.style.display = '';
    btn.textContent = 'Hide extracted text';
  } else {
    div.style.display = 'none';
    btn.textContent = 'Show extracted text';
  }
}

function escapeHtml(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

// --- Enter key in modals ---
document.getElementById('bookTitleInput').addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); document.getElementById('bookAuthorsInput').focus(); } });
document.getElementById('bookAuthorsInput').addEventListener('keydown', e => { if (e.key === 'Enter') createBook(); });
document.getElementById('chapterNameInput').addEventListener('keydown', e => { if (e.key === 'Enter') createChapter(); });
document.getElementById('subchapterNameInput').addEventListener('keydown', e => { if (e.key === 'Enter') createSubchapter(); });

// --- Google Photos Import ---
let pickerPollTimer = null;

async function startGooglePhotosImport() {
  // Check if authenticated
  try {
    const statusRes = await fetch('/google/status');
    const statusData = await statusRes.json();
    if (!statusData.authenticated) {
      window.location.href = '/google/auth';
      return;
    }
  } catch (err) {
    alert('Could not check Google authentication status.');
    return;
  }

  // Show modal and create picker session
  const modal = document.getElementById('googlePickerModal');
  const statusEl = document.getElementById('googlePickerStatus');
  const link = document.getElementById('googlePickerLink');
  const polling = document.getElementById('googlePickerPolling');

  statusEl.textContent = 'Creating picker session...';
  link.style.display = 'none';
  polling.style.display = 'none';
  modal.classList.add('show');

  try {
    const res = await fetch('/google/picker/create', { method: 'POST' });
    const data = await res.json();
    if (!res.ok) {
      statusEl.textContent = data.error || 'Failed to create picker session.';
      return;
    }
    statusEl.textContent = 'Select your photos in the Google Photos tab:';
    link.href = data.pickerUri;
    link.style.display = 'block';
    polling.style.display = 'block';
    pollPickerSession(data.sessionId);
  } catch (err) {
    statusEl.textContent = 'Network error creating picker session.';
  }
}

function pollPickerSession(sessionId) {
  if (pickerPollTimer) clearInterval(pickerPollTimer);
  pickerPollTimer = setInterval(async () => {
    try {
      const res = await fetch(`/google/picker/poll/${sessionId}`);
      const data = await res.json();
      if (!res.ok) {
        clearInterval(pickerPollTimer);
        pickerPollTimer = null;
        document.getElementById('googlePickerStatus').textContent = data.error || 'Polling error.';
        return;
      }
      if (!data.ready) return;

      // Photos selected — stop polling and import
      clearInterval(pickerPollTimer);
      pickerPollTimer = null;
      document.getElementById('googlePickerStatus').textContent = 'Downloading selected photos...';
      document.getElementById('googlePickerLink').style.display = 'none';
      document.getElementById('googlePickerPolling').style.display = 'none';

      const importRes = await fetch('/google/picker/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items: data.items }),
      });
      const importData = await importRes.json();
      document.getElementById('googlePickerModal').classList.remove('show');

      if (!importRes.ok) {
        document.getElementById('statusMsg').className = 'status-msg error';
        document.getElementById('statusMsg').textContent = importData.error || 'Import failed.';
        return;
      }
      pendingFiles = importData.files;
      showFileOrderPanel();
    } catch (err) {
      clearInterval(pickerPollTimer);
      pickerPollTimer = null;
      document.getElementById('googlePickerStatus').textContent = 'Network error while polling.';
    }
  }, 5000);
}

function cancelGooglePicker() {
  if (pickerPollTimer) {
    clearInterval(pickerPollTimer);
    pickerPollTimer = null;
  }
  document.getElementById('googlePickerModal').classList.remove('show');
}

// --- Init on load ---
updateSubchapterSelect();
