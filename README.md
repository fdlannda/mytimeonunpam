# MyTimeOnUNPAM

Sistem informasi pengingat jadwal kuliah real-time untuk mahasiswa Universitas Pamulang (UNPAM) — menampilkan mata kuliah yang sedang berlangsung, dosen pengajar, dan jenis kelas (online/tatap muka) secara otomatis berdasarkan waktu saat ini.

Dibuat untuk Hackathon Universitas Pamulang — Program Studi Teknik Informatika.

## Struktur Project

```
.
├── app.py                  # Logic backend (Flask) — routing, kalkulasi jadwal aktif/berikutnya
├── data/                   # Data jadwal kuliah per kelas (JSON)
├── static/
│   └── style.css           # Styling UI/UX — design system Navy & Gold UNPAM
├── templates/
│   ├── home.html           # Halaman pemilihan jurusan/kelas
│   └── schedule.html       # Halaman dashboard jadwal kuliah
├── requirements.txt        # Dependency Python
└── Procfile                # Konfigurasi deployment (Gunicorn)
```

## Cara Menjalankan Lokal

```bash
pip install -r requirements.txt
python app.py
```

Buka browser ke `http://localhost:5000`.

## Deployment

Project ini siap deploy ke Railway/Render/Heroku menggunakan `Procfile` yang sudah disediakan (Gunicorn sebagai WSGI server).

## Catatan Desain

Sistem badge status waktu (Berlangsung/Berikutnya/Selesai) dan jenis kelas (Online/Tatap Muka) mengikuti design system Navy (#003366) & Gold (#F5A623) UNPAM, dengan prinsip psikologi desain: Gestalt, Hick's Law, Jakob's Law, Cognitive Load Theory, dan Fitts's Law.
