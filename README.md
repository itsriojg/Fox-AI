# 🦊 Fox AI

<p align="center">
  <img src="home-react/public/assets/fox-logo.png" alt="Fox AI Logo" width="120">
</p>

**Chatbot asisten dengan RAG untuk organisasi dan akademik · RAG-powered assistant chatbot for organizations and academics**

---

## 🦊 Project Overview / Tentang Project

**🇮🇩** Fox AI itu chatbot asisten yang gue buat buat jawab pertanyaan seputar organisasi, akademik, dan materi perkuliahan. Konsepnya pakai RAG (Retrieval-Augmented Generation). Jadi gini, dokumen sumber dalam bentuk PDF dipecah jadi potongan kecil (chunk), lalu diubah jadi embedding, terus dicari secara semantik sebelum model AI nyusun jawaban. Setiap pengguna juga punya riwayat chat sendiri yang diisolasi pakai session cookie, jadi nggak saling ngacak.

**🇬🇧** Fox AI is an assistant chatbot I built to answer questions about organizations, academics, and course material. It uses a RAG (Retrieval-Augmented Generation) pipeline: source PDFs are split into small chunks, turned into embeddings, then searched semantically before the AI model writes an answer. Every user also gets their own chat history, isolated via session cookies.

---

## ✨ Features / Fitur Utama

**🇮🇩**
- **RAG pipeline**, jawabannya berbasis dokumen resmi, bukan ngarang.
- **Semantic search**, pencarian FAISS pakai cosine similarity (embedding dinormalisasi).
- **Riwayat per-user**, tiap browser punya history sendiri, bisa dihapus kapan aja.
- **UI bertransisi**, ada animasi circle reveal antara halaman utama dan chatbot.
- **Typing indicator**, ada indikator "AI sedang ngetik" plus auto-scroll.
- **Responsive**, nyaman dipakai di HP maupun laptop.
- **Production-ready**, pake gunicorn sebagai web server plus endpoint health check.

**🇬🇧**
- **RAG pipeline**, answers grounded in official documents, not made up.
- **Semantic search**, FAISS retrieval with cosine similarity (normalized embeddings).
- **Per-user history**, each browser keeps its own history, clearable anytime.
- **Transitional UI**, circle reveal animation between the home page and chatbot.
- **Typing indicator**, "AI is typing" feedback with auto-scroll.
- **Responsive**, works well on phones and laptops.
- **Production-ready**, gunicorn web server plus health check endpoint.

---

## 🛠️ Tech Stack

**🇮🇩** Backend-nya Python (Flask). Buat retrieval pake FAISS + SQLite, embedding dari Jina AI, terus LLM-nya lewat Groq pakai SDK yang OpenAI-compatible. Frontend-nya React (Vite) untuk halaman utama, dan vanilla JavaScript untuk chatbot.

**🇬🇧** Python (Flask) backend. FAISS + SQLite for retrieval, Jina AI for embeddings, and the LLM runs through Groq using an OpenAI-compatible SDK. The frontend is React (Vite) for the home page and vanilla JavaScript for the chatbot.

| Layer | Teknologi |
|---|---|
| Backend | Python 3, Flask 3, gunicorn 23 |
| RAG / Vector | FAISS (IndexIDMap, cosine), numpy |
| Storage | SQLite (history + knowledge) |
| Embedding | Jina AI `jina-embeddings-v5-text-small` (1024-d) |
| LLM | Groq `openai/gpt-oss-120b` (via openai SDK) |
| PDF | pypdf |
| Frontend | React 19 + Vite 8 (home), vanilla JS + CSS (chatbot) |

---

## 🧠 Architecture / How It Works

**🇮🇩**

```
PDF -> clean_text -> chunking (sekitar 800 karakter)
                       |
                       v
                SQLite (chunk + sumber)         FAISS index (embedding)
                       |                                ^
                       |                                |
                       +-----> query -> embedding ------+
                                |
                 context + riwayat |
                                v
                        Prompt -> Groq LLM -> Jawaban
```

1. **Ingestion**, PDF dibaca (pypdf), dibersihin, lalu dipecah jadi chunk sekitar 800 karakter.
2. **Indexing**, tiap chunk di-embedding (Jina), disimpan di SQLite, dan vector-nya masuk ke index FAISS. Pakai `IndexIDMap` biar id-nya sinkron sama database.
3. **Query**, pertanyaan user di-embedding lalu dicari secara cosine (ambil 5 teratas). Chunk yang relevan digabung jadi context.
4. **Generation**, context + riwayat chat (10 pesan terakhir) + system prompt dikirim ke Groq, lalu jawabannya disimpan ke history user.

**🇬🇧**

```
PDF -> clean_text -> chunking (~800 chars)
                       |
                       v
                SQLite (chunk + source)         FAISS index (embedding)
                       |                                ^
                       |                                |
                       +-----> query -> embedding ------+
                                |
                 context + history |
                                v
                        Prompt -> Groq LLM -> Answer
```

1. **Ingestion**, PDFs are read (pypdf), cleaned, and split into ~800-char chunks.
2. **Indexing**, each chunk is embedded (Jina), stored in SQLite, and its vector goes into the FAISS index. `IndexIDMap` keeps the ids in sync with the database.
3. **Query**, the user question is embedded and searched with cosine similarity (top 5). Relevant chunks become the context.
4. **Generation**, context + chat history (last 10 messages) + system prompt are sent to Groq, and the answer is stored in the user's history.

---

## 📱 Full Android Development

**🇮🇩** Ini bagian yang paling bikin project ini beda: seluruh Fox AI dikembangin di dalam Android, bukan di PC.

> Penting: Android di sini itu environment development, bukan platform target. Ini bukan aplikasi Android. Fox AI tetaplah aplikasi web full-stack biasa, cuma kodenya ditulis, dites, dan di-debug dari Android.

**Setup development yang dipakai:**

| Komponen | Alat |
|---|---|
| Linux environment | Termux + Andronix |
| Version control | Git (clone, branch, commit, push ke GitHub) |
| Backend | Python + Flask, virtualenv |
| Frontend | Node.js/npm, Vite, React |
| Code editor (opsional) | Acode |

**Keterbatasan environment yang berhasil diatasi:**
- **Layar kecil dan tanpa mouse**, jadi alurnya keyboard-first dan editor yang ringan.
- **Resource Android terbatas**, jadi build sama index dibuat seefisien mungkin, index FAISS di-load hemat memori.
- **Dependency native**, package kayak `faiss-cpu` di-build dan dites langsung di lingkungan Linux Android.
- **Workflow remote**, semua commit dan push jalan langsung dari Android ke GitHub.

Ini bukan gimmick, ini constraint engineering yang nyata. Setiap fix bug, refactor, dan fitur di repo ini lahir dari Android.

**🇬🇧** This is what makes this project different: the entire Fox AI codebase was developed on an Android device, not on a PC.

> Important: Android here is the development environment, not the target platform. This is not an Android app. Fox AI is still a regular full-stack web application, it just happens to be written, tested, and debugged from Android.

**Development setup used:**

| Component | Tool |
|---|---|
| Linux environment | Termux + Andronix |
| Version control | Git (clone, branch, commit, push to GitHub) |
| Backend | Python + Flask, virtualenv |
| Frontend | Node.js/npm, Vite, React |
| Code editor (optional) | Acode |

**Environment constraints that were overcome:**
- **Small screen and no mouse**, so keyboard-first workflow and lightweight editors.
- **Limited Android resources**, so builds and the index were kept efficient, and the FAISS index is loaded memory-aware.
- **Native dependencies**, packages like `faiss-cpu` are built and tested directly in Android's Linux environment.
- **Remote workflow**, every commit and push goes straight from Android to GitHub.

This isn't a gimmick, it's a real engineering constraint. Every bug fix, refactor, and feature in this repo was born on Android.

---

## 💻 Supported Platforms

**🇮🇩** Karena Fox AI itu aplikasi web biasa, dia bisa dijalankan dan dikembangin di hampir semua platform selama environment dan dependency-nya keinstall:

- **Windows**, Python 3.8+, Node.js (opsional, cuma buat rebuild frontend).
- **macOS**, Python 3.8+, Node.js.
- **Linux**, Python 3.8+, Node.js.
- **Android**, Termux (+ Andronix), Python, Node.js/npm, Git, dan Acode sebagai editor opsional.

Developer lain cukup `git clone` terus ikutin panduan di bawah, bisa langsung dikembangin dari Android dengan cara yang sama.

**🇬🇧** Since Fox AI is a regular web application, it runs and can be developed on almost any platform as long as the environment and dependencies are installed:

- **Windows**, Python 3.8+, Node.js (optional, only to rebuild the frontend).
- **macOS**, Python 3.8+, Node.js.
- **Linux**, Python 3.8+, Node.js.
- **Android**, Termux (+ Andronix), Python, Node.js/npm, Git, and Acode as optional editor.

Other developers can just `git clone` and follow the guide below, and can even develop from Android the exact same way.

---

## 📁 Project Structure

**🇮🇩** Struktur project secara ringkas.

**🇬🇧** Project structure in short.

```
pillow-fox/
├── app.py               # Flask entry point, routes, health check
├── ai.py                # LLM client (Groq via OpenAI-compatible SDK)
├── chatbot.py           # RAG retrieval + prompt assembly
├── rag.py               # PDF ingestion: clean, chunk, embed
├── embedding.py         # Jina embedding client
├── vector_db.py         # FAISS index (cosine-normalized) + rebuild
├── database.py          # SQLite layer (history, knowledge)
├── history.py           # Per-user history helpers
├── knowledge.py         # PDF discovery
├── prompt.py            # System prompt for the AI
├── requirements.txt
├── templates/
│   └── chatbot.html     # Chatbot UI (vanilla JS)
├── static/              # chatbot.css, chatbot.js, assets
├── home-react/          # React home page (Vite), builds to dist/
└── knowledge/pdf/       # Source documents (PDFs)
```

---

## 🚀 Installation & Usage

**🇮🇩** Cara install dan jalankan.

**🇬🇧** How to install and run.

```bash
# 1. Clone
git clone https://github.com/itsriojg/Fox-AI.git
cd Fox-AI

# 2. Backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # isi API key-nya, lihat tabel di bawah

# 3. Frontend (opsional, cuma kalau ubah halaman React)
cd home-react
npm install
npm run build
cd ..

# 4. Jalankan (mode development)
python app.py                   # buka http://localhost:5000

# 5. Jalankan (mode production)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Cek health: `curl http://localhost:5000/health` -> `{"status":"ok"}`.

---

## 🔐 Environment Variables

**🇮🇩** Variabel environment dibaca dari file `.env` di root project.

**🇬🇧** Environment variables are read from a `.env` file in the project root.

| Variable | Wajib | Deskripsi / Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Kunci sesi Flask (session cookie) / Flask session secret |
| `JINA_API_KEY` | ✅ | Kunci API Jina AI (embedding) / Jina AI API key |
| `GROQ_API_KEY` | ✅ | Kunci API Groq (LLM) / Groq API key |
| `GROQ_BASE_URL` | ✅ | Base URL endpoint Groq / Groq endpoint base URL |
| `HOST` | Tidak | Host bind, default `0.0.0.0` |
| `PORT` | Tidak | Port bind, default `5000` |

`SECRET_KEY` otomatis digenerate kalau kosong, biar session tetap aman di dev.

---

## 🧪 Testing

**🇮🇩** Project ini belum punya test suite otomatis (pytest/unittest). Sejauh ini pengujiannya verifikasi manual end-to-end lewat HTTP:

- Cek semua route utama (`/`, `/chatbot`, `/health`, `/api/chat`, `/clear`).
- Isolasi history antar-user, dua session beda dikirim pesan dan dipastiin nggak saling bocor. Hapus history satu user nggak nyentuh user lain.
- Verifikasi RAG, query jalan, context keambil, dan jawaban model balik.
- Verifikasi index FAISS, rebuild index dari database dan konsistensi id (via `IndexIDMap`).

**🇬🇧** The project does not have an automated test suite (pytest/unittest) yet. So far testing has been manual end-to-end verification over HTTP:

- Check all main routes (`/`, `/chatbot`, `/health`, `/api/chat`, `/clear`).
- Per-user history isolation, two separate sessions send messages and are verified not to leak into each other. Clearing one user's history doesn't touch another's.
- RAG verification, queries flow through, context is retrieved, and the model answer comes back.
- FAISS verification, index rebuild from the database and id consistency (via `IndexIDMap`).

---

## 📚 Development Journey

**🇮🇩** Perjalanan project ini (62+ commits) nunjukin evolusi teknis yang beneran:

1. **Dari template jadi full-stack**, layout chatbot dasar, terus responsive, terus UI/UX lengkap.
2. **Migrasi integrasi AI**, dari fetch API langsung ke SDK OpenAI-compatible, dengan timeout dan error handling yang makin rapi.
3. **RAG pipeline dari nol**, PDF ke chunk ke FAISS, terus di-harden: mapping id SQLite ke FAISS pakai `IndexIDMap`, normalisasi embedding (cosine), dan proses build knowledge yang aman dari kegagalan.
4. **Frontend React**, halaman utama pindah ke React (Vite) dengan animasi circle reveal ke chatbot.
5. **Multi-user**, history chat dipisah per user pakai session cookie, lengkap dengan migrasi tabel otomatis.
6. **Production-ready**, gunicorn, health check, dan bind host/port lewat environment.

**🇬🇧** The project journey (62+ commits) shows a real technical evolution:

1. **From template to full-stack**, basic chatbot layout, then responsive, then complete UI/UX.
2. **AI integration migration**, from raw fetch API to the OpenAI-compatible SDK, with better timeout and error handling.
3. **RAG pipeline from scratch**, PDF to chunk to FAISS, then hardened: SQLite to FAISS id mapping with `IndexIDMap`, embedding normalization (cosine), and a failure-safe knowledge build.
4. **React frontend**, the home page moved to React (Vite) with a circle reveal transition to the chatbot.
5. **Multi-user**, chat history isolated per user with session cookies, including automatic table migration.
6. **Production-ready**, gunicorn, health check, and host/port binding via environment.

---

## 💡 What I Learned

**🇮🇩**
- Ngerakit pipeline RAG end-to-end, dari dokumen mentah sampai jawaban yang berbasis data.
- Troubleshooting vektor dan database, sinkronisasi id FAISS ke SQLite, normalisasi embedding, dan strategi atomic write.
- Ngatur sesi dan privacy user, pakai session cookie dan migrasi skema database.
- Nulis kode production-grade dari environment yang terbatas, disiplin commit, error handling, dan verifikasi manual yang sistematis.

**🇬🇧**
- Building a full RAG pipeline, from raw documents to grounded answers.
- Vector and database troubleshooting, FAISS to SQLite id sync, embedding normalization, and atomic-write strategies.
- Managing sessions and user privacy with session cookies and database schema migration.
- Writing production-grade code from a constrained environment, with commit discipline, error handling, and systematic manual verification.

---

## 🔮 Future Improvements

**🇮🇩** Ide yang realistis buat dilanjutin:

- Tambah test suite otomatis (pytest) buat endpoint dan RAG.
- Migrasi database ke PostgreSQL buat skala lebih gede dan concurrency tulis lebih tinggi.
- Fitur unggah dokumen lewat UI (folder `uploads/` udah disiapin).
- Migrasi halaman chatbot ke React biar satu codebase.
- Rate limiting di endpoint chat.

**🇬🇧** Realistic ideas to continue with:

- Add an automated test suite (pytest) for endpoints and RAG.
- Migrate to PostgreSQL for larger scale and higher write concurrency.
- Document upload feature via the UI (the `uploads/` folder is already in place).
- Migrate the chatbot page to React for a single codebase.
- Rate limiting on the chat endpoint.

---

## 👤 Author

**🇮🇩** Dibuat oleh [itsriojg](https://github.com/itsriojg). Seluruh project dibangun dari Android, dari commit pertama sampai sekarang.

**🇬🇧** Built by [itsriojg](https://github.com/itsriojg). The entire project was built on Android, from the very first commit to now.

---

<p align="center">
  <sub>🦊 Built entirely on Android · Dibangun sepenuhnya di Android</sub>
</p>