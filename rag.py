from pypdf import PdfReader
from knowledge import get_path_pdf_files
from database import clear_knowledge, insert_knowledge
from vector_db import simpan_index, rebuild_faiss
from embedding import get_embedding
import os
import re


def read_pdf(path):
  reader = PdfReader(path)
  text = ""
  for page in reader.pages:
    text = text + page.extract_text() + "\n"
  return text
  
def index_pdf():
  paths = get_path_pdf_files()
  index_files = []
  for path in paths:
   file = os.path.basename(path)
   judul_and_pdf = os.path.splitext(file)
   judul = judul_and_pdf[0]
   index_file = {
    "judul" : judul,
    "path" : path
   }
   index_files.append(index_file)
  return index_files
    
HEADING_PAT = r"(?m)^\s*([1-6])\.\s+(Apa itu HIMATIF[^\n]*|Sejarah HIMATIF[^\n]*|Visi dan Misi[^\n]*|Keanggotaan[^\n]*|Struktur Kepengurusan[^\n]*|Identitas Organisasi[^\n]*)"

JABATAN = {
  "Ketua",
  "Wakil Ketua",
  "Sekretaris",
  "Bendahara",
  "Departemen Keorganisasian",
  "Departemen PSDM (Pemberdayaan Sumber Daya Mahasiswa)",
  "Departemen Komunikasi dan Informasi (Kominfo)",
  "Departemen Litbang (Penelitian & Pengembangan)",
  "Departemen Danus (Dana & Usaha)",
}

def _clean_block(block):
  block = re.sub(r"Departemen\s*\n\s*Keorganisasian", "Departemen Keorganisasian", block)
  block = re.sub(r"\(Pemberdayaan Sumber\s*\n\s*Daya Mahasiswa\)", "(Pemberdayaan Sumber Daya Mahasiswa)", block)
  block = re.sub(r"Departemen Komunikasi\s*\n\s*dan Informasi \(Kominfo\)", "Departemen Komunikasi dan Informasi (Kominfo)", block)
  block = re.sub(r"\(Penelitian &\s*\n\s*Pengembangan\)", "(Penelitian & Pengembangan)", block)
  block = re.sub(r"Departemen Danus \(Dana\s*\n\s*& Usaha\)", "Departemen Danus (Dana & Usaha)", block)
  lines = [re.sub(r" +", " ", l.strip()) for l in block.split("\n")]
  lines = [l for l in lines if l]
  items = []
  buf = ""
  for line in lines:
    if line in JABATAN:
      if buf.strip():
        items.append(buf.strip())
      buf = line
    elif line.startswith("•"):
      if buf.strip():
        items.append(buf.strip())
      buf = line
    elif re.match(r"^[1-9]\.\s+[A-Z0-9]", line):
      if buf.strip():
        items.append(buf.strip())
      buf = line
    elif re.match(r"^o [A-Z]", line):
      if buf.strip():
        items.append(buf.strip())
      buf = line
    else:
      if buf in JABATAN:
        buf = buf + ": " + line
      else:
        buf = (buf + " " + line).strip() if buf else line
  if buf.strip():
    items.append(buf.strip())
  return "\n".join(items).strip()

def make_chunks(text, target=1100, group=700, min_len=30):
  matches = list(re.finditer(HEADING_PAT, text))
  if not matches:
    body = _clean_block(text)
    return [body] if len(body) >= min_len else []
  chunks = []
  for i, m in enumerate(matches):
    num = m.group(1)
    title = re.sub(r"\s+", " ", m.group(2).strip())
    start = m.start()
    end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
    body = re.sub(HEADING_PAT, "", text[start:end], count=1).strip()
    body = _clean_block(body)
    if not body or len(body) < min_len:
      continue
    prefix = f"[Bab {num} - {title}]"
    full = f"{prefix}\n{body}"
    if len(full) <= target or "\n" not in body:
      chunks.append(full)
      continue
    items = [x.strip() for x in body.split("\n") if x.strip()]
    buf = ""
    part = 1
    for it in items:
      cand = (buf + "\n" + it).strip() if buf else it
      if len(prefix) + 1 + len(cand) <= group or not buf:
        buf = cand
      else:
        chunks.append(f"{prefix} (bagian {part})\n{buf}")
        part += 1
        buf = it
    if buf and len(buf) >= min_len:
      label = f"{prefix} (bagian {part})" if part > 1 else prefix
      chunks.append(f"{label}\n{buf}")
  return chunks

def clean_text(text):
  text = text.strip().replace("\r", "\n")
  text = re.sub(r"[\t]+", " ", text)
  text = re.sub(r" *\n *", "\n", text)
  text = re.sub(r"\n{3,}", "\n\n", text)
  text = re.sub(r"(?m)^Jabatan Tugas & Wewenang Utama\s*\n?", "", text)
  text = text.replace("—", "-").replace("–", "-")
  text = re.sub(r"(\w) -(\w)", r"\1-\2", text)
  text = re.sub(r"\bTekn ologi\b", "Teknologi", text)
  text = re.sub(r"\bTek nologi\b", "Teknologi", text)
  text = re.sub(r"\bja wab\b", "jawab", text)
  text = re.sub(r"\by ang\b", "yang", text)
  text = re.sub(r"\bmenge depankan\b", "mengedepankan", text)
  text = re.sub(r"\bakti f\b", "aktif", text)
  text = text.encode("utf-16", "surrogatepass").decode("utf-16", "ignore")
  return text.strip()
  
def build_knowledge():
  paths = get_path_pdf_files()
  if not paths:
    print("[WARN] Tidak ada file PDF untuk dibangun knowledge")
    return

  sources = []
  chunks = []
  for path in paths:
    try:
      text = read_pdf(path)
    except Exception as e:
      print(f"[WARN] Gagal membaca PDF {path}: {e}")
      continue
    text = clean_text(text)
    if not text:
      continue
    source = os.path.splitext(os.path.basename(path))[0]
    for chunk in make_chunks(text):
      sources.append(source)
      chunks.append(chunk)

  if not chunks:
    print("[WARN] Tidak ada chunk yang berhasil dibuat")
    return

  try:
    vectors = []
    for chunk in chunks:
      vectors.append(get_embedding(chunk))
  except RuntimeError as e:
    print(f"[ERROR] Gagal membuat embedding: {e}")
    return

  try:
    clear_knowledge()
    ids = []
    for i, chunk in enumerate(chunks):
      ids.append(insert_knowledge(sources[i], chunk))

    try:
      simpan_index(ids, vectors)
    except Exception as e:
      print(f"[ERROR] Gagal menyimpan index: {e}, mencoba rebuild dari database")
      rebuild_faiss()
  except Exception as e:
    print(f"[ERROR] Gagal menyimpan knowledge: {e}")
  
