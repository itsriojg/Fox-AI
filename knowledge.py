import os
from pypdf import PdfReader

def get_pdf_files():
  folder_file = "knowledge/pdf"
  files = os.listdir(folder_file)
  
  path_file = []
  
  for file in files:
    file = os.path.join(folder_file, file)
    path_file.append(file)
    
  return path_file
  