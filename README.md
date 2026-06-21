# 🎓 MTOU — Sistem Monitoring Jadwal Perkuliahan Universitas Pamulang

<div align="center">

**Sistem Monitoring Jadwal Akademik Real-Time**

[![Flask](https://img.shields.io/badge/Flask-2.0+-red)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

Sistem informasi pengingat jadwal kuliah real-time untuk mahasiswa Universitas Pamulang (UNPAM) — menampilkan mata kuliah yang sedang berlangsung, dosen pengajar, dan jenis kelas (online/tatap muka) secara otomatis berdasarkan waktu saat ini.

🚀 **Live Demo**: [Linktree](https://linktr.ee/mytimeonunpam)

</div>

---

## 📋 Daftar Isi

- [🌟 Fitur](#-fitur)
- [🏗️ Arsitektur](#️-arsitektur)
- [🧠 Algoritma Inti](#-algoritma-inti)
- [🎨 Sistem Desain](#-sistem-desain)
- [📊 Struktur Data](#-struktur-data)
- [🔧 Instalasi](#-instalasi)
- [🚀 Deployment](#-deployment)
- [🤝 Kontribusi](#-kontribusi)
- [📝 Lisensi](#-lisensi)

---

## 🌟 Fitur

### Monitoring Jadwal Real-Time
- **Deteksi Kelas Aktif**: Mengidentifikasi secara otomatis kelas yang sedang berlangsung dengan masa tenggang 5 menit
- **Prediksi Kelas Berikutnya**: Algoritma cerdas untuk memprediksi kelas yang akan datang sepanjang minggu
- **Timer Hitung Mundur**: Hitung mundur real-time untuk kelas saat ini dan yang akan datang

### Sistem Mode Akademik Cerdas
- **Mode Berbasis SKS**: Untuk kelas Reg A/B, mode ditentukan oleh SKS (3 SKS = hybrid, 2 SKS = offline saja)
- **Mode Berbasis Periode**: Untuk kelas Reg CK/CS, pergantian mode otomatis berdasarkan tanggal UTS/UAS
- **Periode Tradisional**: Fallback ke sistem minggu ganjil/genap untuk jenis kelas lain

### Pelacakan Progres Akademik
- **Progres Semester**: Progress bar visual menunjukkan persentase penyelesaian semester
- **Informasi Minggu**: Minggu akademik saat ini dengan detail mode akademik
- **Fase Akademik**: Indikasi jelas pra-UTS dan pasca-UTS

### UI/UX Modern
- **Mode Gelap**: Dukungan mode gelap penuh dengan persistensi tema otomatis
- **Desain Responsif**: Dioptimalkan untuk desktop, tablet, dan perangkat mobile
- **Animasi Halus**: Animasi masuk dan transisi interaktif
- **Branding UNPAM**: Skema warna Navy (#003366) & Gold (#F5A623)

---

## 🏗️ Arsitektur

### Teknologi yang Digunakan

```
┌─────────────────────────────────────────────────────────┐
│                    Lapisan Frontend                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  home.html   │  │ schedule.html│  │  style.css   │  │
│  │  (Seleksi)   │  │  (Dashboard) │  │  (Styling)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Lapisan Backend                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │          Aplikasi Flask (app.py)                 │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │  │
│  │  │ Routing  │  │ Logika   │  │ Data     │      │  │
│  │  │ Engine   │  │ Engine   │  │ Loader   │      │  │
│  │  └──────────┘  └──────────┘  └──────────┘      │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Lapisan Data                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │        File Jadwal JSON (data/)                   │  │
│  │  jurusan_semester_kelas.json                       │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Struktur Project

```
mytimeonunpam/
├── app.py                  # Aplikasi Flask utama dengan logika inti
├── requirements.txt        # Dependensi Python
├── Procfile               # Konfigurasi deployment (Gunicorn)
├── data/                  # File jadwal JSON per kelas
│   ├── Teknik_Informatika_1_A.json
│   ├── Teknik_Informatika_1_B.json
│   └── ...
├── static/
│   ├── style.css          # Stylesheet utama dengan sistem desain
│   └── images/            # Aset statis (logo, ikon)
│       ├── universitas-pamulang-logo-png_seeklogo-259632.png
│       └── unpam-logo.png
└── templates/
    ├── home.html          # Halaman seleksi kelas
    └── schedule.html      # Halaman dashboard jadwal
```

---

## 🧠 Algoritma Inti

### 1. Manajemen Zona Waktu

```python
WIB = timezone(timedelta(hours=7))
```

Semua perhitungan waktu menggunakan Waktu Indonesia Barat (WIB, UTC+7) untuk memastikan akurasi jadwal akademik Indonesia.

### 2. Penentuan Mode Akademik

Sistem mengimplementasikan tiga strategi mode akademik yang berbeda:

#### A. Mode Berbasis SKS (Reg A/B)
```python
if reguler in REG_AB:
    return item.get("mode", "Tatap Muka")
```
- **3 SKS**: Mode hybrid (sesi offline + online)
- **2 SKS**: Offline saja
- Mode sudah ditentukan di data JSON

#### B. Mode Berbasis Periode (Reg CK/CS)
```python
if reguler in REG_CK_CS:
    periode_saat_ini = 1 if sekarang < uts_date else 2
    if periode_json == 1:
        return "Tatap Muka" if periode_saat_ini == 1 else "Online"
    else:
        return "Online" if periode_saat_ini == 1 else "Tatap Muka"
```
- Pergantian mode otomatis setelah UTS
- Periode 1 (pra-UTS): Mengikuti definisi periode JSON
- Periode 2 (pasca-UTS): Membalikkan mode

#### C. Periode Tradisional Ganjil/Genap
```python
if minggu_ke % 2 == 0:
    if periode == 1:
        return "Online"
    return "Tatap Muka"
```
- Minggu genap: Periode 1 = Online, Periode 2 = Offline
- Minggu ganjil: Periode 1 = Offline, Periode 2 = Online

### 3. Deteksi Kelas Aktif

```python
def get_active_slot_keys(data):
    grace_period = timedelta(minutes=5)
    if (mulai - grace_period) <= sekarang <= selesai:
        active_keys.add((slot["hari"], slot["jam_mulai"], slot["jam_selesai"]))
```

**Logika Masa Tenggang**: Kelas dianggap aktif 5 menit sebelum waktu mulai yang dijadwalkan untuk mengakomodasi kedatangan awal dan keterlambatan ringan.

### 4. Algoritma Prediksi Kelas Berikutnya

```python
def get_next_class(data):
    # 1. Cari hari berikutnya dengan jadwal
    for slot in slots:
        selisih_hari = (HARI_MAP[hari] - sekarang.weekday()) % 7
        if selisih_hari < min_selisih_hari:
            hari_berikutnya = hari
            min_selisih_hari = selisih_hari
    
    # 2. Hitung countdown untuk setiap kelas pada hari itu
    for item in items:
        item["countdown"] = int((target - sekarang).total_seconds())
    
    # 3. Urutkan berdasarkan countdown dan kembalikan 8 teratas
    hasil.sort(key=lambda item: item["countdown"])
    return hasil[:8]
```

**Langkah Algoritma**:
1. Identifikasi hari berikutnya dengan jadwal kelas
2. Hitung selisih waktu untuk setiap kelas pada hari itu
3. Urutkan berdasarkan kedekatan dan kembalikan 8 kelas terdekat yang akan datang
4. Tangani kasus edge: jika semua kelas hari ini sudah selesai, default ke Senin depan

### 5. Perhitungan Progres Semester

```python
def get_progress(data):
    total_hari = (semester_selesai - semester_mulai).days
    hari_berlalu = (sekarang - semester_mulai).days
    persen = round((hari_berlalu / total_hari) * 100)
    return min(persen, 100)
```

Menghitung persentase penyelesaian semester berdasarkan hari yang berlalu vs durasi total semester.

### 6. Perhitungan Minggu Akademik

```python
def get_global_week(data):
    minggu_ke = ((sekarang - semester_mulai).days // 7) + 1
    return max(minggu_ke, 1)
```

Menentukan minggu akademik saat ini dengan menghitung periode 7 hari dari tanggal mulai semester.

---

## 🎨 Sistem Desain

### Palet Warna

```css
--navy: #003366          /* Warna merek utama */
--gold: #F5A623          /* Warna aksen */
--gold-surface: #FEF3DC  /* Latar belakang emas terang */
--text-soft: #5C6680     /* Teks sekunder (mode terang) */
--bg: #FFFFFF            /* Latar belakang (mode terang) */
--panel: #FFFFFF         /* Latar belakang panel (mode terang) */
```

### Warna Mode Gelap

```css
--bg: #0A1424            /* Latar belakang gelap */
--panel: #002244         /* Panel gelap */
--text: #E2E8F0          /* Teks utama */
--text-soft: #94A3B8     /* Teks sekunder */
--line: rgba(245, 166, 35, 0.12)  /* Garis emas halus */
```

### Tipografi

- **Judul**: Source Serif 4 (serif)
- **Isi**: Inter (sans-serif)
- **Ukuran responsif**: Menggunakan `clamp()` untuk tipografi fluid

### Prinsip Desain

1. **Prinsip Gestalt**: Pengelompokan elemen terkait untuk hierarki visual
2. **Hukum Hick**: Meminimalkan pilihan untuk mengurangi kelumpuhan keputusan
3. **Hukum Jakob**: Mengikuti pola yang familiar untuk kenyamanan pengguna
4. **Teori Beban Kognitif**: Menyajikan informasi dalam potongan yang dapat dicerna
5. **Hukum Fitts**: Mengoptimalkan elemen interaktif untuk seleksi mudah

### Animasi

- **Masukan Eyebrow**: Fade-in dengan efek slide-up dan scale (0.8s)
- **Progress Bar**: Animasi fill halus (0.6s ease)
- **Toggle Tema**: Pergantian tema instan dengan transisi ikon
- **Hover Tombol**: Angkat halus dan peningkatan bayangan

---

## 📊 Struktur Data

### Format File Jadwal JSON

```json
{
  "semester_mulai": "2026-02-17",
  "semester_selesai": "2026-07-04",
  "uts_date": "2026-05-15",
  "uas_date": "2026-07-04",
  "reguler": "A",
  "jadwal": [
    {
      "hari": "Senin",
      "jam_mulai": "08:00",
      "jam_selesai": "10:00",
      "mata_kuliah": "Algoritma dan Struktur Data",
      "dosen": "Dr. Ahmad Fauzi",
      "ruang": "A-301",
      "mode": "offline",
      "periode": 1
    }
  ]
}
```

### Deskripsi Field

- **semester_mulai**: Hari pertama semester
- **semester_selesai**: Hari terakhir semester
- **uts_date**: Tanggal ujian tengah semester
- **uas_date**: Tanggal ujian akhir semester
- **reguler**: Jenis kelas (A, B, CK, CS)
- **jadwal**: Array entri jadwal
  - **hari**: Hari dalam minggu (Senin-Minggu)
  - **jam_mulai**: Waktu mulai kelas (HH:MM)
  - **jam_selesai**: Waktu selesai kelas (HH:MM)
  - **mata_kuliah**: Nama mata kuliah
  - **dosen**: Nama dosen
  - **ruang**: Nomor ruangan
  - **mode**: Mode kelas (offline/online)
  - **periode**: Penugasan periode (1 atau 2)

---

## 🔧 Instalasi

### Prasyarat

- Python 3.8 atau lebih tinggi
- pip (manajer paket Python)

### Pengembangan Lokal

1. **Clone repository**
```bash
git clone https://github.com/yourusername/mytimeonunpam.git
cd mytimeonunpam
```

2. **Instal dependensi**
```bash
pip install -r requirements.txt
```

3. **Siapkan direktori data**
```bash
mkdir data
# Tambahkan file jadwal JSON Anda ke direktori data/
```

4. **Jalankan aplikasi**
```bash
python app.py
```

5. **Akses aplikasi**
```
Buka browser ke: http://localhost:5000
```

### Dependensi

```
Flask==2.3.0
Werkzeug==2.3.0
```

---

## 🚀 Deployment

### Railway

1. Push kode ke GitHub
2. Hubungkan repository ke Railway
3. Railway akan otomatis mendeteksi aplikasi Flask
4. Atur variabel lingkungan jika diperlukan
5. Deploy!

### Render

1. Push kode ke GitHub
2. Buat Web Service baru di Render
3. Hubungkan repository GitHub
4. Konfigurasi pengaturan build:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Deploy!

### Heroku

1. Instal Heroku CLI
2. Login ke Heroku
```bash
heroku login
```

3. Buat aplikasi
```bash
heroku create your-app-name
```

4. Deploy
```bash
git push heroku main
```

### Procfile

```
web: gunicorn app:app
```

---

## 🤝 Kontribusi

Kontribusi sangat diterima! Silakan ikuti pedoman ini:

1. **Fork repository**
2. **Buat cabang fitur**
```bash
git checkout -b feature/amazing-feature
```

3. **Commit perubahan Anda**
```bash
git commit -m 'Tambah fitur luar biasa'
```

4. **Push ke cabang**
```bash
git push origin feature/amazing-feature
```

5. **Buka Pull Request**

### Pedoman Pengembangan

- Ikuti gaya kode yang ada
- Tambahkan komentar untuk algoritma kompleks
- Uji secara menyeluruh sebelum mengirim
- Perbarui dokumentasi sesuai kebutuhan

---

## 📝 Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT - lihat file LICENSE untuk detail.

---

## 🙏 Ucapan Terima Kasih

- **Universitas Pamulang** untuk data akademik dan dukungan
- **Program Studi Teknik Informatika** untuk kesempatan hackathon
- **Unpam Nexus** untuk kolaborasi pengembangan

---

## 📞 Kontak

Untuk pertanyaan, saran, atau kolaborasi:
- **Linktree**: [https://linktr.ee/mytimeonunpam](https://linktr.ee/mytimeonunpam)

---

<div align="center">

**Dibuat dengan ❤️ oleh Unpam Nexus**

© 2026 MTOU — Sistem Monitoring Jadwal Perkuliahan Universitas Pamulang

</div>
