# 🎓 MTOU — Sistem Monitoring Jadwal Perkuliahan Universitas Pamulang

<div align="center">

**Real-time Academic Schedule Monitoring System**

[![Flask](https://img.shields.io/badge/Flask-2.0+-red)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

Sistem informasi pengingat jadwal kuliah real-time untuk mahasiswa Universitas Pamulang (UNPAM) — menampilkan mata kuliah yang sedang berlangsung, dosen pengajar, dan jenis kelas (online/tatap muka) secara otomatis berdasarkan waktu saat ini.

🚀 **Live Demo**: [Linktree](https://linktr.ee/mytimeonunpam)

</div>

---

## 📋 Table of Contents

- [🌟 Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🧠 Core Algorithms](#-core-algorithms)
- [🎨 Design System](#-design-system)
- [📊 Data Structure](#-data-structure)
- [🔧 Installation](#-installation)
- [🚀 Deployment](#-deployment)
- [🤝 Contributing](#-contributing)
- [📝 License](#-license)

---

## 🌟 Features

### Real-Time Schedule Monitoring
- **Live Class Detection**: Automatically identifies currently active classes with 5-minute grace period
- **Next Class Prediction**: Intelligent algorithm to predict upcoming classes across the week
- **Countdown Timer**: Real-time countdown for both current and upcoming classes

### Smart Academic Mode System
- **SKS-Based Mode**: For Reg A/B classes, mode determined by credit hours (3 SKS = hybrid, 2 SKS = offline only)
- **Period-Based Mode**: For Reg CK/CS classes, automatic mode switching based on UTS/UAS dates
- **Traditional Period**: Fallback to odd/even week system for other class types

### Academic Progress Tracking
- **Semester Progress**: Visual progress bar showing semester completion percentage
- **Week Information**: Current academic week with academic mode details
- **Academic Phases**: Clear indication of pre-UTS and post-UTS periods

### Modern UI/UX
- **Dark Mode**: Full dark mode support with automatic theme persistence
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Smooth Animations**: Entrance animations and interactive transitions
- **UNPAM Branding**: Navy (#003366) & Gold (#F5A623) color scheme

---

## 🏗️ Architecture

### Technology Stack

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  home.html   │  │ schedule.html│  │  style.css   │  │
│  │  (Selection) │  │  (Dashboard) │  │  (Styling)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Backend Layer                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │              Flask Application (app.py)           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │  │
│  │  │ Routing  │  │ Logic    │  │ Data     │      │  │
│  │  │ Engine   │  │ Engine   │  │ Loader   │      │  │
│  │  └──────────┘  └──────────┘  └──────────┘      │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Data Layer                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │           JSON Schedule Files (data/)             │  │
│  │  jurusan_semester_kelas.json                       │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Project Structure

```
mytimeonunpam/
├── app.py                  # Main Flask application with core logic
├── requirements.txt        # Python dependencies
├── Procfile               # Deployment configuration (Gunicorn)
├── data/                  # JSON schedule files per class
│   ├── Teknik_Informatika_1_A.json
│   ├── Teknik_Informatika_1_B.json
│   └── ...
├── static/
│   ├── style.css          # Main stylesheet with design system
│   └── images/            # Static assets (logos, icons)
│       ├── universitas-pamulang-logo-png_seeklogo-259632.png
│       └── unpam-logo.png
└── templates/
    ├── home.html          # Class selection page
    └── schedule.html      # Schedule dashboard page
```

---

## 🧠 Core Algorithms

### 1. Time Zone Management

```python
WIB = timezone(timedelta(hours=7))
```

All time calculations use Indonesia Western Time (WIB, UTC+7) to ensure accuracy for Indonesian academic schedules.

### 2. Academic Mode Determination

The system implements three different academic mode strategies:

#### A. SKS-Based Mode (Reg A/B)
```python
if reguler in REG_AB:
    return item.get("mode", "Tatap Muka")
```
- **3 SKS**: Hybrid mode (offline + online sessions)
- **2 SKS**: Offline only
- Mode is pre-defined in JSON data

#### B. Period-Based Mode (Reg CK/CS)
```python
if reguler in REG_CK_CS:
    periode_saat_ini = 1 if sekarang < uts_date else 2
    if periode_json == 1:
        return "Tatap Muka" if periode_saat_ini == 1 else "Online"
    else:
        return "Online" if periode_saat_ini == 1 else "Tatap Muka"
```
- Automatically switches modes after UTS
- Periode 1 (pre-UTS): Follows JSON period definition
- Periode 2 (post-UTS): Inverts the mode

#### C. Traditional Odd/Even Week
```python
if minggu_ke % 2 == 0:
    if periode == 1:
        return "Online"
    return "Tatap Muka"
```
- Even weeks: Period 1 = Online, Period 2 = Offline
- Odd weeks: Period 1 = Offline, Period 2 = Online

### 3. Active Class Detection

```python
def get_active_slot_keys(data):
    grace_period = timedelta(minutes=5)
    if (mulai - grace_period) <= sekarang <= selesai:
        active_keys.add((slot["hari"], slot["jam_mulai"], slot["jam_selesai"]))
```

**Grace Period Logic**: Classes are considered active 5 minutes before the scheduled start time to account for early arrivals and slight delays.

### 4. Next Class Prediction Algorithm

```python
def get_next_class(data):
    # 1. Find next day with schedule
    for slot in slots:
        selisih_hari = (HARI_MAP[hari] - sekarang.weekday()) % 7
        if selisih_hari < min_selisih_hari:
            hari_berikutnya = hari
            min_selisih_hari = selisih_hari
    
    # 2. Calculate countdown for each class on that day
    for item in items:
        item["countdown"] = int((target - sekarang).total_seconds())
    
    # 3. Sort by countdown and return top 8
    hasil.sort(key=lambda item: item["countdown"])
    return hasil[:8]
```

**Algorithm Steps**:
1. Identify the next day with scheduled classes
2. Calculate time difference for each class on that day
3. Sort by proximity and return the 8 nearest upcoming classes
4. Handle edge case: if all today's classes are done, default to next Monday

### 5. Semester Progress Calculation

```python
def get_progress(data):
    total_hari = (semester_selesai - semester_mulai).days
    hari_berlalu = (sekarang - semester_mulai).days
    persen = round((hari_berlalu / total_hari) * 100)
    return min(persen, 100)
```

Calculates the percentage of semester completion based on elapsed days vs total semester duration.

### 6. Academic Week Calculation

```python
def get_global_week(data):
    minggu_ke = ((sekarang - semester_mulai).days // 7) + 1
    return max(minggu_ke, 1)
```

Determines the current academic week by counting 7-day periods from semester start date.

---

## 🎨 Design System

### Color Palette

```css
--navy: #003366          /* Primary brand color */
--gold: #F5A623          /* Accent color */
--gold-surface: #FEF3DC  /* Light gold background */
--text-soft: #5C6680     /* Secondary text (light mode) */
--bg: #FFFFFF            /* Background (light mode) */
--panel: #FFFFFF         /* Panel background (light mode) */
```

### Dark Mode Colors

```css
--bg: #0A1424            /* Dark background */
--panel: #002244         /* Dark panel */
--text: #E2E8F0          /* Primary text */
--text-soft: #94A3B8     /* Secondary text */
--line: rgba(245, 166, 35, 0.12)  /* Subtle gold lines */
```

### Typography

- **Headings**: Source Serif 4 (serif)
- **Body**: Inter (sans-serif)
- **Responsive sizing**: Uses `clamp()` for fluid typography

### Design Principles

1. **Gestalt Principle**: Grouping related elements for visual hierarchy
2. **Hick's Law**: Minimizing choices to reduce decision paralysis
3. **Jakob's Law**: Following familiar patterns for user comfort
4. **Cognitive Load Theory**: Presenting information in digestible chunks
5. **Fitts's Law**: Optimizing interactive elements for easy selection

### Animations

- **Eyebrow Entrance**: Fade-in with slide-up and scale effect (0.8s)
- **Progress Bar**: Smooth fill animation (0.6s ease)
- **Theme Toggle**: Instant theme switching with icon transition
- **Button Hover**: Subtle lift and shadow enhancement

---

## 📊 Data Structure

### JSON Schedule File Format

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

### Field Descriptions

- **semester_mulai**: First day of semester
- **semester_selesai**: Last day of semester
- **uts_date**: Mid-term exam date
- **uas_date**: Final exam date
- **reguler**: Class type (A, B, CK, CS)
- **jadwal**: Array of schedule entries
  - **hari**: Day of week (Senin-Minggu)
  - **jam_mulai**: Class start time (HH:MM)
  - **jam_selesai**: Class end time (HH:MM)
  - **mata_kuliah**: Course name
  - **dosen**: Lecturer name
  - **ruang**: Room number
  - **mode**: Class mode (offline/online)
  - **periode**: Period assignment (1 or 2)

---

## 🔧 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/mytimeonunpam.git
cd mytimeonunpam
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Prepare data directory**
```bash
mkdir data
# Add your JSON schedule files to the data/ directory
```

4. **Run the application**
```bash
python app.py
```

5. **Access the application**
```
Open browser to: http://localhost:5000
```

### Dependencies

```
Flask==2.3.0
Werkzeug==2.3.0
```

---

## 🚀 Deployment

### Railway

1. Push code to GitHub
2. Connect repository to Railway
3. Railway will automatically detect Flask app
4. Set environment variables if needed
5. Deploy!

### Render

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect GitHub repository
4. Configure build settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Deploy!

### Heroku

1. Install Heroku CLI
2. Login to Heroku
```bash
heroku login
```

3. Create app
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

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**
```bash
git checkout -b feature/amazing-feature
```

3. **Commit your changes**
```bash
git commit -m 'Add amazing feature'
```

4. **Push to the branch**
```bash
git push origin feature/amazing-feature
```

5. **Open a Pull Request**

### Development Guidelines

- Follow the existing code style
- Add comments for complex algorithms
- Test thoroughly before submitting
- Update documentation as needed

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Universitas Pamulang** for the academic data and support
- **Program Studi Teknik Informatika** for the hackathon opportunity
- **Unpam Nexus** for development collaboration

---

## 📞 Contact

For questions, suggestions, or collaboration:
- **Linktree**: [https://linktr.ee/mytimeonunpam](https://linktr.ee/mytimeonunpam)
- **Email**: contact@unpam.ac.id

---

<div align="center">

**Built with ❤️ by Unpam Nexus**

© 2026 MTOU — Sistem Monitoring Jadwal Perkuliahan Universitas Pamulang

</div>
