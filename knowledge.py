import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path_pdf_files():
  folder_file = os.path.join(BASE_DIR, "knowledge", "pdf")

  if not os.path.isdir(folder_file):
    print(f"[WARN] Folder knowledge/pdf tidak ditemukan: {folder_file}")
    return []

  path_file = []

  for file in os.listdir(folder_file):
    if file.lower().endswith(".pdf"):
      path_file.append(os.path.join(folder_file, file))

  return path_file