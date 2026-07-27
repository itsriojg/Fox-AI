from pypdf import PdfReader
from knowledge import get_path_pdf_files
from database import clear_knowledge, insert_knowledge
from vector_db import rebuild_faiss
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
  clear_knowledge()
  paths = get_path_pdf_files()
  for path in paths:
    text = read_pdf(path)
    text = clean_text(text)
    chunks = make_chunks(text)
    source = os.path.splitext(os.path.basename(path))[0]
    for chunk in chunks:
      insert_knowledge(source, chunk)
  rebuild_faiss()
  
