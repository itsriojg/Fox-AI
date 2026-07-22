from pypdf import PdfReader
from knowledge import get_path_pdf_files
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
   
def pilih_pdf(message):
  index_files = index_pdf()
  paths = []
  for file in index_files:
    if file["judul"] in message:
      file_path = file["path"]
      paths.append(file_path)
  return paths  
    
def brain_knowledge(message):
  paths = pilih_pdf(message)
  if paths != []:
    knowledge = ""
    for files in paths:
      hasil_baca = read_pdf(files)
      chunks = make_chunks(hasil_baca)
      knowledge += hasil_baca
    return knowledge
  else:
    files = get_path_pdf_files()
    knowledge = ""
    for file in files:
      knowledge = knowledge + read_pdf(file)
    return knowledge
    
def make_chunks(text):
  chunks = []
  current_chunk = ""
  paragraphs = text.split("\n")
  for paragraph in paragraphs:
    if len(current_chunk) + len(paragraph) <= 800:
      current_chunk += paragraph
    else:
      chunks.append(current_chunk)
      current_chunk = paragraph
  if current_chunk != "":
    chunks.append(current_chunk)
  
  return chunks

def clean_text(text):
  text = text.strip()
  re.sub(r"[\t]+", " ", text)
  text = re.sub(r"\n{3,}", "\n\n", text)
  return text
  