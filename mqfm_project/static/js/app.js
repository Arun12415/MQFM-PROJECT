const docType = document.getElementById('docType');
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const preview = document.getElementById('preview');
const previewImg = document.getElementById('previewImg');
const fileNameEl = document.getElementById('fileName');
const fileMetaEl = document.getElementById('fileMeta');
const clearBtn = document.getElementById('clearBtn');
const processBtn = document.getElementById('processBtn');
const processBtnText = document.getElementById('processBtnText');
const spinner = document.getElementById('spinner');
const resultCard = document.getElementById('resultCard');
const resultTitle = document.getElementById('resultTitle');
const rowCount = document.getElementById('rowCount');
const resultTable = document.getElementById('resultTable');
const statusPill = document.getElementById('statusPill');
const errorBox = document.getElementById('errorBox');
const footnote = document.getElementById('footnote');
let currentFile = null;

['dragover', 'dragenter'].forEach(evt =>
  dropzone.addEventListener(evt, e => { e.preventDefault(); dropzone.classList.add('drag'); })
);
['dragleave', 'drop'].forEach(evt =>
  dropzone.addEventListener(evt, e => { e.preventDefault(); dropzone.classList.remove('drag'); })
);
dropzone.addEventListener('drop', e => {
  if (e.dataTransfer.files.length) {
    fileInput.files = e.dataTransfer.files;
    handleFile(e.dataTransfer.files[0]);
  }
});
fileInput.addEventListener('change', () => {
  if (fileInput.files.length) handleFile(fileInput.files[0]);
});

function handleFile(file) {
  currentFile = file;
  const reader = new FileReader();
  reader.onload = e => { previewImg.src = e.target.result; };
  reader.readAsDataURL(file);
  fileNameEl.textContent = file.name;
  fileMetaEl.textContent = (file.type || "image") + " · " + Math.round(file.size / 1024) + " KB";
  preview.classList.add('show');
  processBtn.disabled = false;
  resultCard.classList.add('hidden');
  errorBox.classList.add('hidden');
}

clearBtn.addEventListener('click', () => {
  currentFile = null;
  fileInput.value = "";
  preview.classList.remove('show');
  processBtn.disabled = true;
});

processBtn.addEventListener('click', async () => {
  if (!currentFile) return;
  setLoading(true);
  errorBox.classList.add('hidden');

  const formData = new FormData();
  formData.append('document', currentFile);
  formData.append('doc_type', docType.value);

  try {
    const res = await fetch('/upload', { method: 'POST', body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Processing failed");
    renderResult(data);
    resultCard.classList.remove('hidden');
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  } catch (err) {
    errorBox.textContent = err.message;
    errorBox.classList.remove('hidden');
  } finally {
    setLoading(false);
  }
});

function setLoading(isLoading) {
  processBtn.disabled = isLoading;
  spinner.classList.toggle('hidden', !isLoading);
  processBtnText.textContent = isLoading ? "Processing…" : "Process document";
}

function renderResult(data) {
  resultTitle.textContent = data.doc_label + " — Result";
  rowCount.textContent = data.row_count + (data.row_count === 1 ? " row read" : " rows read");
  statusPill.textContent = data.overall_status;
  statusPill.className = "status-pill " + (data.overall_status === "PASSED" ? "passed" : "failed");
  footnote.innerHTML = `Rows are appended to the <b>${data.doc_label}</b> sheet in <code>production_log.xlsx</code> on the server.`;

  const columns = [...data.fields, "validation_status"];
  const colLabels = columns.map(f => f === "validation_status" ? "Status" : (data.labels[f] || f));

  let html = "<thead><tr>" + colLabels.map(l => `<th>${l}</th>`).join("") + "</tr></thead><tbody>";
  data.rows.forEach(row => {
    html += "<tr>" + columns.map(f => {
      if (f === "validation_status") {
        const cls = row[f] === "PASSED" ? "passed" : "failed";
        return `<td class="status-cell ${cls}">${row[f]}</td>`;
      }
      return `<td>${row[f] ?? ''}</td>`;
    }).join("") + "</tr>";
  });
  html += "</tbody>";
  resultTable.innerHTML = html;
}

document.getElementById('anotherBtn').addEventListener('click', () => {
  resultCard.classList.add('hidden');
  preview.classList.remove('show');
  processBtn.disabled = true;
  currentFile = null;
  fileInput.value = "";
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

document.getElementById('downloadBtn').addEventListener('click', () => {
  window.location.href = '/download';
});
