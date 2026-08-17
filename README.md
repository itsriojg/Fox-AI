# 🦊 Fox AI

<p align="center">
  <img src="home-react/public/assets/fox-logo.png" alt="Fox AI Logo" width="120">
</p>

Fox AI adalah chatbot asisten berbasis RAG (Retrieval‑Augmented Generation) yang dirancang untuk menjawab pertanyaan terkait organisasi, lingkungan akademik, dan materi perkuliahan. Jawaban dihasilkan berdasarkan dokumen sumber (misalnya PDF) yang diindeks sehingga mengurangi risiko halusinasi model.

---

## Fitur Utama

- RAG pipeline: jawaban berbasis dokumen sumber.
- Pencarian semantik: retrieval menggunakan FAISS dengan cosine similarity (embedding dinormalisasi).
- Riwayat per pengguna: setiap browser menyimpan riwayat obrolan sendiri; riwayat dapat dihapus.
- Antarmuka transisi: animasi circle reveal antara halaman utama dan chatbot.
- Indikator pengetikan: feedback "AI sedang mengetik" dengan auto-scroll.
- Responsif: tampilan dioptimalkan untuk perangkat seluler dan desktop.
- Siap untuk produksi: menggunakan gunicorn dan waitress sebagai web server serta menyediakan health check endpoint.

---

## Teknologi

- Backend: Python 3, Flask 3, gunicorn, waitress
- Retrieval / vektor: FAISS (IndexIDMap, cosine), numpy
- Penyimpanan: SQLite (history + knowledge)
- Embedding: Jina AI `jina-embeddings-v5-text-small` (1024-d)
- LLM: Groq (`openai/gpt-oss-120b`) melalui SDK yang kompatibel OpenAI
- PDF processing: pypdf
- Frontend: React 19 + Vite 8 (halaman home); chatbot menggunakan vanilla JS + CSS

---

## Arsitektur dan Alur Kerja

Alur utama:
PDF → pembersihan teks → pemecahan menjadi chunk (~800 karakter) → embedding (Jina) → penyimpanan chunk dan metadata di SQLite → vektor disimpan di FAISS (IndexIDMap).

Saat query:
1. Pertanyaan pengguna di‑embedding.
2. Pencarian FAISS (cosine) mengembalikan top‑5 chunk relevan.
3. Chunk relevan digabung menjadi konteks; konteks + riwayat obrolan (10 pesan terakhir) + system prompt dikirim ke Groq LLM.
4. Jawaban yang dihasilkan disimpan ke riwayat pengguna.

Diagram sederhana:
PDF -> clean_text -> chunking (~800 chars)
                   ↓
           SQLite (chunk + sumber)    FAISS index (embedding)
                   ↑                          ↓
               query -> embedding -> konteks + riwayat -> Prompt -> Groq LLM -> Jawaban

---

## Pengembangan di Lingkungan Android (Catatan Khusus)

Seluruh pengembangan proyek ini dilakukan dari lingkungan Android (Termux + Andronix), bukan berarti aplikasi ini adalah aplikasi Android. Fox AI tetap merupakan aplikasi web full‑stack; keunikan proyek adalah semua pembuatan, pengujian, dan debugging dilakukan dari perangkat Android.

Alat dan konfigurasi pengembangan yang digunakan:
- Lingkungan Linux di Android: Termux + Andronix
- Version control: Git
- Backend: Python + virtualenv
- Frontend: Node.js / npm, Vite, React
- Editor opsional: Acode

Kendala yang diatasi:
- Antarmuka layar kecil → workflow keyboard‑first dan editor ringan.
- Resource terbatas → optimasi memori untuk FAISS dan efisiensi build.
- Dependensi native → pembangunan `faiss-cpu` dan dependensi lainnya langsung di lingkungan Linux pada Android.
- Alur kerja remote → commit dan push langsung dari Android ke GitHub.

---

## Platform yang Didukung

Aplikasi dapat dijalankan di platform berikut selama dependensi terpenuhi:

| Platform | Status | Catatan |
|---|:---:|---|
| Windows | ✅ Didukung | Mode pengembangan (`python app.py`); untuk produksi gunakan **waitress** atau WSL |
| macOS | ✅ Didukung | Mode pengembangan dan produksi (gunicorn) |
| Linux | ✅ Didukung | Mode pengembangan dan produksi (gunicorn) |
| Android | ✅ Didukung | Termux (+ Andronix), Python, Node.js/npm, Git, editor opsional |

Catatan penting: gunicorn tidak berjalan native di Windows karena bergantung pada fitur Unix (`fcntl`/`fork`). Oleh karena itu, waitress ditambahkan ke `requirements.txt` sebagai alternatif produksi di Windows.

Kontributor dapat melakukan `git clone` dan mengikuti panduan instalasi untuk menyiapkan lingkungan pengembangan, termasuk pengembangan dari Android.

---

## Struktur Proyek (Ringkasan)

pillow-fox/
├── app.py               # Entrypoint Flask: route & health check
├── ai.py                # Klien LLM (Groq via OpenAI-compatible SDK)
├── chatbot.py           # RAG retrieval + perakitan prompt
├── rag.py               # Ingest PDF: pembersihan, chunking, embedding
├── embedding.py         # Klien embedding Jina
├── vector_db.py         # Manajemen FAISS (cosine-normalized) + rebuild
├── database.py          # Lapisan SQLite (history, knowledge)
├── history.py           # Helper untuk riwayat per-user
├── knowledge.py         # Penemuan dokumen sumber
├── prompt.py            # System prompt untuk AI
├── requirements.txt
├── templates/
│   └── chatbot.html     # UI chatbot (vanilla JS)
├── static/              # chatbot.css, chatbot.js, assets
├── home-react/          # React home page (Vite), build ke dist/
└── knowledge/pdf/       # Dokumen sumber (PDF)

---

## Instalasi & Penggunaan

1. Clone repository
```bash
git clone https://github.com/itsriojg/Fox-AI.git
cd Fox-AI
```

2. Siapkan virtual environment dan instal dependensi backend
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # isi variabel environment sesuai penjelasan di bawah
```

3. (Opsional) Build frontend jika melakukan perubahan pada React
```bash
cd home-react
npm install
npm run build
cd ..
```

4. Menjalankan dalam mode pengembangan
```bash
python app.py                   # akses http://localhost:5000
```

5. Menjalankan dalam mode produksi (Linux / macOS)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

6. Menjalankan dalam mode produksi (Windows)
```bash
waitress-serve --listen=0.0.0.0:5000 app:app
```

Cek health endpoint:
```bash
curl http://localhost:5000/health
# Response: {"status":"ok"}
```

---

## Variabel Lingkungan

Variabel dibaca dari file `.env` pada root proyek.

| Variable        | Wajib | Deskripsi |
|---|:---:|---|
| SECRET_KEY      | ✅ | Kunci sesi Flask (Flask session secret) |
| JINA_API_KEY    | ✅ | Kunci API Jina AI untuk embedding |
| GROQ_API_KEY    | ✅ | Kunci API Groq untuk LLM |
| GROQ_BASE_URL   | ✅ | Base URL endpoint Groq |
| HOST            | Tidak | Host bind, default `0.0.0.0` |
| PORT            | Tidak | Port bind, default `5000` |

Catatan: Pada mode pengembangan, `SECRET_KEY` akan digenerasi otomatis jika tidak disediakan.

---

## Pengujian

Saat ini proyek belum memiliki test suite otomatis (mis. pytest atau unittest). Pengujian yang dilakukan bersifat manual end‑to‑end melalui HTTP. Berikut hasil pengujian terkini.

### Isolasi Riwayat per Pengguna (5 Pengguna)

| Skenario | Hasil |
|---|---|
| 5 pengguna masing‑masing mengirim 1 pesan | 5 user_id unik, 10 baris database (5 pesan + 5 balasan AI) |
| Setiap pengguna membuka halaman chatbot | Hanya pesan miliknya sendiri yang tampil, tidak ada kebocoran antar‑pengguna |
| Salah satu pengguna menghapus riwayat | Hanya riwayat milik pengguna tersebut yang hilang; pengguna lain tetap utuh |
| Pengguna yang menghapus setelahnya | Riwayat kosong; pengguna lain tetap memiliki pesannya |

Kesimpulan: isolasi riwayat antar‑pengguna berjalan sempurna. Setiap browser mendapatkan ID unik melalui session cookie, sehingga banyak pengguna tetap memiliki riwayat masing‑masing tanpa saling memengaruhi.

### Responsif Perangkat Seluler vs Desktop

Layout bersifat fleksibel (menggunakan `dvh`, flexbox, dan persentase). Pada layar kecil (`max-width: 768px`), bubble pesan menggunakan lebar 85% dengan ukuran font 14px; pada layar besar, bubble maksimal 75% dengan ukuran font 15px. Satu catatan yang sempat ditemukan: font Poppins dideklarasikan di CSS tetapi belum di‑load, sehingga sempat jatuh ke fallback `sans-serif`. Hal ini telah diperbaiki dengan menambahkan link Google Fonts di kedua halaman.

### Kompatibilitas Sistem Operasi

Seluruh dependency terverifikasi tersedia untuk macOS, Windows, dan Linux, termasuk `faiss-cpu` 1.14.3 yang menyediakan wheel untuk ketiga platform tersebut. Gunicorn terverifikasi tidak berjalan native di Windows, sehingga waitress ditambahkan sebagai alternatif produksi. Kode bebas dari hardcoded path OS dan menggunakan `os.path.join`, sehingga aman lintas platform.

---

## Perjalanan Pengembangan

Proyek ini telah berkembang melalui lebih dari 60 commit, mencakup:
1. Evolusi dari template menjadi aplikasi full‑stack dengan UI/UX responsif.
2. Migrasi integrasi AI dari panggilan API mentah ke SDK OpenAI‑compatible beserta perbaikan handling timeout/error.
3. Pembangunan RAG pipeline end‑to‑end dan penguatan sinkronisasi ID antara SQLite dan FAISS.
4. Frontend React: halaman utama dipindahkan ke React (Vite) dengan circle reveal transition ke chatbot.
5. Multi‑user: riwayat chat dipisah per pengguna menggunakan session cookie.
6. Persiapan untuk deployment produksi (gunicorn, waitress, health check, konfigurasi host/port via env).

---

## Pelajaran Utama

- Membangun pipeline RAG yang lengkap dari dokumen mentah hingga jawaban yang tergrounded.
- Mengatasi sinkronisasi ID antara FAISS dan SQLite serta normalisasi embedding.
- Menangani sesi pengguna dan privasi menggunakan session cookie serta migrasi skema database.
- Menulis kode produksi dari lingkungan dengan keterbatasan sumber daya, khususnya pengembangan di Android.

---

## Rencana Perbaikan (Roadmap)

- Menambahkan test suite otomatis (pytest) untuk endpoint dan komponen RAG.
- Memigrasi penyimpanan ke PostgreSQL untuk skala dan concurrency lebih baik.
- Menyediakan fitur unggah dokumen melalui antarmuka pengguna (folder `uploads/` telah disiapkan).
- Memigrasikan halaman chatbot ke React sehingga frontend menjadi satu codebase.
- Menambahkan rate limiting pada endpoint chat.
- Menyediakan Dockerfile / instruksi Docker untuk mempermudah deployment (terutama untuk dependensi native seperti FAISS).

---

## Penulis

Dibuat oleh [itsriojg](https://github.com/itsriojg). Seluruh proyek dikembangkan dari perangkat Android sejak awal.

<p align="center">
  <sub>🦊 Dibangun sepenuhnya di Android</sub>
</p>
