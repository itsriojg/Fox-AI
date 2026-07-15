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
    
def brain_knowledge():
  files = get_path_pdf_files()
  knowledge = ""
  for file in files:
    knowledge = knowledge + read_pdf(file)
  return knowledge