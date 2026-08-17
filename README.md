# 🦊 Fox AI

<p align="center">
  <img src="home-react/public/assets/fox-logo.png" alt="Fox AI Logo" width="120">
</p>

**RAG-powered AI assistant for new students (HIMATIF) · Asisten AI berbasis RAG untuk mahasiswa baru (HIMATIF)**

---

## 🦊 Project Overview / Tentang Project

**🇮🇩** Fox AI adalah chatbot asisten pembelajaran yang menjawab pertanyaan seputar organisasi HIMATIF, akademik, dan materi perkuliahan. Dibangun dengan arsitektur RAG (Retrieval-Augmented Generation): dokumen sumber (PDF) diolah menjadi *chunks*, di-embedding, lalu dicari secara semantik sebelum jawaban disusun oleh model AI. Setiap pengguna memiliki riwayat chat sendiri yang diisolasi memakai session cookie.

**🇬🇧** Fox AI is a learning assistant chatbot that answers questions about the HIMATIF organization, academics, and course material. Built on a RAG (Retrieval-Augmented Generation) pipeline: source documents (PDFs) are split into chunks, embedded, and retrieved semantically before the AI model composes an answer. Every user gets their own isolated chat history via session cookies.

---

## ✨ Features / Fitur Utama

**🇮🇩**
- **RAG pipeline** — jawaban berbasis dokumen resmi, bukan mengarang.
- **Semantic search** — pencarian FAISS dengan *cosine similarity* (embedding dinormalisasi).
- **Riwayat per-user** — tiap browser/device punya history sendiri, bisa dihapus kapan saja.
- **UI bertransisi** — animasi *circle reveal* antara halaman utama dan chatbot.
- **Typing indicator** — indikator "AI sedang mengetik" + auto-scroll.
- **Responsive** — nyaman di HP maupun laptop.
- **Production-ready** — gunicorn web server + endpoint health check.

**🇬🇧**
- **RAG pipeline** — answers grounded in official documents, not hallucinated.
- **Semantic search** — FAISS retrieval with cosine similarity (normalized embeddings).
- **Per-user history** — each browser/device keeps its own history, clearable anytime.
- **Transitional UI** — circle-reveal animation between the home page and chatbot.
- **Typing indicator** — "AI is typing" feedback with auto-scroll.
- **Responsive** — comfortable on phones and laptops.
- **Production-ready** — gunicorn web server + health check endpoint.

---

## 🛠️ Tech Stack

**🇮🇩** Backend Python (Flask), retrieval FAISS + SQLite, embedding Jina AI, LLM via Groq (SDK OpenAI-compatible), frontend React (Vite) + vanilla JavaScript.

**🇬🇧** Python backend (Flask), FAISS + SQLite retrieval, Jina AI embeddings, LLM via Groq (OpenAI-compatible SDK), React (Vite) + vanilla JavaScript frontend.

| Layer | Teknologi |
|---|---|
| Backend | Python 3, Flask 3, gunicorn 23 |
| RAG / Vector | FAISS (IndexIDMap, cosine), numpy |
| Storage | SQLite (history + knowledge) |
| Embedding | Jina AI — `jina-embeddings-v5-text-small` (1024-d) |
| LLM | Groq — `openai/gpt-oss-120b` (via `openai` SDK) |
| PDF | pypdf |
| Frontend | React 19 + Vite 8 (home), vanilla JS + CSS (chatbot) |

---

## 🧠 Architecture / How It Works

**🇮🇩**

```
PDF ──► clean_text ──► chunking (~800 karakter)
        │
        ▼
  SQLite (chunk + sumber)          FAISS index (embedding)
        │                                  ▲
        │                                  │
        └──── RAG lookup ──► query ──► embedding
                                      │
                    context + riwayat │
                                      ▼
                               Prompt ──► Groq LLM ──► Jawaban
```

1. **Ingestion** — PDF dibaca (`pypdf`), dibersihkan, dipecah jadi chunk ±800 karakter.
2. **Indexing** — tiap chunk di-embedding (Jina), disimpan di SQLite, vector-nya masuk index FAISS (`IndexIDMap` untuk sinkronisasi id).
3. **Query** — pertanyaan user di-embedding, dicari secara *cosine* (top-5), chunk relevan digabung jadi context.
4. **Generation** — context + riwayat chat (10 pesan terakhir) + system prompt dikirim ke Groq; jawaban disimpan ke history user.

**🇬🇧**

```
PDF ──► clean_text ──► chunking (~800 chars)
        │
        ▼
  SQLite (chunk + source)           FAISS index (embedding)
        │                                  ▲
        │                                  │
        └──── RAG lookup ──► query ──► embedding
                                      │
                    context + history │
                                      ▼
                               Prompt ──► Groq LLM ──► Answer
```

1. **Ingestion** — PDFs are read (`pypdf`), cleaned, and split into ~800-char chunks.
2. **Indexing** — each chunk is embedded (Jina), stored in SQLite, with its vector added to a FAISS index (`IndexIDMap` for id syncing).
3. **Query** — the user question is embedded and searched with cosine similarity (top-5); relevant chunks become context.
4. **Generation** — context + chat history (last 10 messages) + system prompt are sent to Groq; the answer is stored in the user's history.

---

## 📱 Full Android Development

**🇮🇩** Ini bagian yang paling membedakan project ini: **seluruh Fox AI dikembangkan di dalam Android** — bukan di PC.

> Penting: Android di sini adalah **environment development**, bukan platform target. Ini bukan "aplikasi Android". Fox AI tetaplah aplikasi web full-stack biasa — hanya saja kodenya ditulis, dites, dan di-debug dari dalam HP.

**Setup development yang dipakai:**

| Komponen | Alat |
|---|---|
| Linux environment | Termux + Andronix |
| Version control | Git (clone, branch, commit, push ke GitHub) |
| Backend | Python + Flask, virtualenv |
| Frontend | Node.js/npm, Vite, React |
| Code editor (opsional) | Acode |

**Keterbatasan environment yang berhasil diatasi:**
- **Layar kecil & tanpa mouse** — UI terminal, alur kerja *keyboard-first*, dan editor ringan.
- **Resource HP terbatas** — build & index dibikin efisien; FAISS index di-load hemat memori.
- **Dependency native** — package seperti `faiss-cpu` di-build & diuji langsung di lingkungan Linux HP.
- **Workflow remote** — semua commit & push jalan langsung dari HP menuju GitHub.

Ini bukan gimmick — ini *engineering constraint* yang nyata. Setiap fix bug, refactor, dan fitur di repo ini diproduksi dari HP.

**🇬🇧** This is what sets the project apart: **the entire Fox AI codebase was developed on an Android device** — not on a PC.

> Important: Android here is the **development environment**, not the target platform. This is not an "Android app". Fox AI is a standard full-stack web application — it just happens to be written, tested, and debugged from a phone.

**Development setup used:**

| Component | Tool |
|---|---|
| Linux environment | Termux + Andronix |
| Version control | Git (clone, branch, commit, push to GitHub) |
| Backend | Python + Flask, virtualenv |
| Frontend | Node.js/npm, Vite, React |
| Code editor (optional) | Acode |

**Environment constraints that were overcome:**
- **Small screen & no mouse** — terminal-first UI, keyboard-driven workflow, lightweight editors.
- **Limited phone resources** — efficient builds; the FAISS index is loaded memory-aware.
- **Native dependencies** — packages like `faiss-cpu` built and tested directly in the phone's Linux environment.
- **Remote workflow** — every commit and push goes straight from the phone to GitHub.

This isn't a gimmick — it's a real engineering constraint. Every bug fix, refactor, and feature in this repo was produced from a phone.

---

## 💻 Supported Platforms

**🇮🇩** Karena Fox AI adalah aplikasi web standar, ia bisa **dijalankan dan dikembangkan di hampir semua platform** selama environment & dependency-nya terpasang:

- **Windows** — Python 3.8+, Node.js (opsional, untuk rebuild frontend).
- **macOS** — Python 3.8+, Node.js.
- **Linux** — Python 3.8+, Node.js.
- **Android** — Termux (+ Andronix), Python, Node.js/npm, Git; Acode sebagai editor opsional.

Developer lain cukup `git clone` lalu ikuti panduan instalasi di bawah — bisa langsung dikembangkan dari Android dengan cara yang sama.

**🇬🇧** Since Fox AI is a standard web application, it **runs and can be developed on almost any platform** as long as the environment and dependencies are installed:

- **Windows** — Python 3.8+, Node.js (optional, only to rebuild the frontend).
- **macOS** — Python 3.8+, Node.js.
- **Linux** — Python 3.8+, Node.js.
- **Android** — Termux (+ Andronix), Python, Node.js/npm, Git; Acode as optional editor.

Other developers can just `git clone` and follow the install guide below — and even develop from Android the exact same way.

---

## 📁 Project Structure

**🇮🇩** Struktur ringkas project.

**🇬🇧** Concise project structure.

```
pillow-fox/
├── app.py               # Flask entry point, routes, health check
├── ai.py                # LLM client (Groq via OpenAI-compatible SDK)
├── chatbot.py           # RAG retrieval + prompt assembly
├── rag.py               # PDF ingestion: clean → chunk → embed
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
├── home-react/          # React home page (Vite) → builds to dist/
└── knowledge/pdf/       # Source documents (PDFs)
```

---

## 🚀 Installation & Usage

**🇮🇩** Instalasi dan cara menjalankan.

**🇬🇧** Installation and usage.

```bash
# 1. Clone
git clone https://github.com/itsriojg/Fox-AI.git
cd Fox-AI

# 2. Backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # isi kunci API-nya (lihat tabel di bawah)

# 3. Frontend (opsional — hanya jika mengubah halaman React)
cd home-react
npm install
npm run build
cd ..

# 4. Jalankan (mode development)
python app.py                   # → http://localhost:5000

# 5. Jalankan (mode production)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Cek health: `curl http://localhost:5000/health` → `{"status":"ok"}`.

---

## 🔐 Environment Variables

**🇮🇩** Variabel environment dibaca dari `.env` di root project.

**🇬🇧** Environment variables are read from a `.env` file in the project root.

| Variable | Wajib | Deskripsi / Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Kunci sesi Flask (session cookie) / Flask session secret |
| `JINA_API_KEY` | ✅ | Kunci API Jina AI (embedding) / Jina AI API key |
| `GROQ_API_KEY` | ✅ | Kunci API Groq (LLM) / Groq API key |
| `GROQ_BASE_URL` | ✅ | Base URL endpoint Groq / Groq endpoint base URL |
| `HOST` | — | Host bind, default `0.0.0.0` |
| `PORT` | — | Port bind, default `5000` |

`SECRET_KEY` otomatis digenerate jika kosong (agar session tetap aman di dev).

---

## 🧪 Testing

**🇮🇩** Project ini belum memiliki test suite otomatis (pytest/unittest). Pengujian yang dilakukan sejauh ini adalah **verifikasi manual end-to-end** via HTTP:

- Cek semua route utama (`/`, `/chatbot`, `/health`, `/api/chat`, `/clear`).
- Isolasi history antar-user — dua session berbeda dikirim pesan, dipastikan tidak saling bocor; hapus history satu user tidak menyentuh history user lain.
- Verifikasi RAG — query diteruskan, context terambil, dan jawaban model kembali.
- Verifikasi index FAISS — rebuild index dari database dan konsistensi id (via `IndexIDMap`).

**🇬🇧** The project does not have an automated test suite (pytest/unittest) yet. Testing so far has been **manual end-to-end verification** over HTTP:

- Check all main routes (`/`, `/chatbot`, `/health`, `/api/chat`, `/clear`).
- Per-user history isolation — two separate sessions send messages and are verified not to leak into each other; clearing one user's history does not touch another's.
- RAG verification — queries flow through, context is retrieved, and the model answer comes back.
- FAISS verification — index rebuild from the database and id consistency (via `IndexIDMap`).

---

## 📚 Development Journey

**🇮🇩** Perjalanan project (62+ commits) menceritakan evolusi teknis yang nyata:

1. **Dari template ke full-stack** — layout chatbot dasar, lalu responsive, lalu UI/UX lengkap.
2. **Migrasi integrasi AI** — dari `fetch` API langsung, ke SDK OpenAI-compatible, dengan timeout & error handling yang matang.
3. **RAG pipeline dari nol** — PDF → chunk → FAISS, lalu diperbaiki: mapping id SQLite↔FAISS dengan `IndexIDMap`, normalisasi embedding (cosine), dan proses build knowledge yang aman dari kegagalan.
4. **Frontend React** — halaman utama dipindah ke React (Vite), dengan animasi *circle reveal* ke chatbot.
5. **Multi-user** — history chat dipisah per user memakai session cookie, lengkap dengan migrasi tabel otomatis.
6. **Production-readiness** — gunicorn, health check, binding host/port via environment.

**🇬🇧** The project journey (62+ commits) tells a real technical evolution:

1. **From template to full-stack** — basic chatbot layout, then responsive, then complete UI/UX.
2. **AI integration migration** — from raw `fetch` API to the OpenAI-compatible SDK, with solid timeout & error handling.
3. **RAG pipeline from scratch** — PDF → chunk → FAISS, then hardened: SQLite↔FAISS id mapping with `IndexIDMap`, embedding normalization (cosine), and a failure-safe knowledge build process.
4. **React frontend** — the home page moved to React (Vite) with a circle-reveal transition to the chatbot.
5. **Multi-user** — chat history isolated per user with session cookies, including automatic table migration.
6. **Production-readiness** — gunicorn, health check, host/port binding via environment.

---

## 💡 What I Learned

**🇮🇩**
- Merakit **pipeline RAG end-to-end**: dari dokumen mentah sampai jawaban yang berbasis data.
- **Troubleshooting vektor & database**: sinkronisasi id FAISS↔SQLite, normalisasi embedding, dan strategi atomic write.
- **Mengelola sesi & privacy user** dengan session cookie dan migrasi skema database.
- **Menulis kode production-grade** dari environment yang terbatas — disiplin commit, error handling, dan verifikasi manual yang sistematis.

**🇬🇧**
- Building a **full RAG pipeline**: from raw documents to grounded answers.
- **Vector & database troubleshooting**: FAISS↔SQLite id sync, embedding normalization, and atomic-write strategies.
- **Managing sessions & user privacy** with session cookies and database schema migration.
- **Writing production-grade code** from a constrained environment — commit discipline, error handling, and systematic manual verification.

---

## 🔮 Future Improvements

**🇮🇩** Ide yang realistis untuk dilanjutkan:
- Tambah **test suite otomatis** (pytest) untuk endpoint & RAG.
- Migrasi database ke **PostgreSQL** untuk skala lebih besar & concurrency tulis lebih tinggi.
- Fitur **unggah dokumen** melalui UI (struktur folder `uploads/` sudah disiapkan).
- Migrasi halaman **chatbot ke React** agar satu codebase.
- **Rate limiting** pada endpoint chat.

**🇬🇧** Realistic ideas to continue with:
- Add an **automated test suite** (pytest) for endpoints & RAG.
- Migrate to **PostgreSQL** for larger scale and higher write concurrency.
- **Document upload** feature via the UI (the `uploads/` folder structure is already in place).
- Migrate the **chatbot page to React** for a single codebase.
- **Rate limiting** on the chat endpoint.

---

## 👤 Author

**🇮🇩** Dikembangkan oleh [itsriojg](https://github.com/itsriojg). Seluruh project dibangun dari Android — dari commit pertama sampai sekarang.

**🇬🇧** Built by [itsriojg](https://github.com/itsriojg). The entire project was built from an Android device — from the very first commit to now.

---

<p align="center">
  <sub>🦊 Built entirely on Android · Dibangun sepenuhnya di Android</sub>
</p>
