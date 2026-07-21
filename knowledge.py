import os
from pypdf import PdfReader

def get_path_pdf_files():
  folder_file = "knowledge/pdf"
  files = os.listdir(folder_file)
  
  path_file = []
  
  for file in files:
    file = os.path.join(folder_file, file)
    path_file.append(file)
    
  return path_file
  
def read_pdf(path):
  reader = PdfReader(path)
  text = ""
  for page in reader.pages:
    text = text + page.extract_text() + "\n"
  return text
    
def brain_knowledge(message):
  paths = pilih_pdf(message)
  if paths != []:
    knowledge = ""
    for files in paths:
      hasil_baca = read_pdf(files)
      knowledge += hasil_baca
    print("PDF terpilih:", paths)
    return knowledge
  else:
    files = get_path_pdf_files()
    knowledge = ""
    for file in files:
      knowledge = knowledge + read_pdf(file)
    return knowledge
  
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