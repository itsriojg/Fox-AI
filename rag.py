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
    
def make_chunks(text):
  chunks = []
  current_chunk = ""
  paragraphs = text.split("\n")
  for paragraph in paragraphs:
    if len(current_chunk) + len(paragraph) <= 800:
      current_chunk += paragraph + "\n"
    else:
      chunks.append(current_chunk)
      current_chunk = paragraph
  if current_chunk != "":
    chunks.append(current_chunk)
  
  return chunks

def clean_text(text):
  text = text.strip()
  text = re.sub(r"[\t]+", " ", text)
  text = re.sub(r"\n{3,}", "\n\n", text)
  text = text.encode("utf-16", "surrogatepass").decode("utf-16", "ignore")
  return text
  
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
  
