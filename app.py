import os
import json
from datetime import datetime, timedelta, timezone
from flask import (
    Flask,
    render_template,
    request,
    redirect
)

# Indonesia/WIB timezone (UTC+7)
WIB = timezone(timedelta(hours=7))

app = Flask(__name__)

HARI_MAP = {
    "Senin": 0,
    "Selasa": 1,
    "Rabu": 2,
    "Kamis": 3,
    "Jumat": 4,
    "Sabtu": 5,
    "Minggu": 6
}

REG_AB = {"A", "B"}
REG_CK_CS = {"CK", "CS"}


# ==========================
# DATA
# ==========================

def get_available_classes():

    classes = []

    if not os.path.exists("data"):
        return classes

    for file in os.listdir("data"):

        if not file.endswith(".json"):
            continue

        try:

            jurusan, semester, kelas = (
                file.replace(".json", "")
                .split("_")
            )

            classes.append({
                "jurusan": jurusan,
                "semester": semester,
                "kelas": kelas
            })

        except:
            pass

    return classes


def load_data(
    jurusan,
    semester,
    kelas
):

    file_path = (
        f"data/"
        f"{jurusan}_{semester}_{kelas}.json"
    )

    with open(
        file_path,
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ==========================
# MODE ONLINE / OFFLINE
# ==========================

def get_mode(
    item,
    minggu_ke,
    reguler,
    data=None
):

    # Reguler A/B: mode ditentukan oleh SKS, bukan minggu ganjil/genap.
    # 3 SKS = ada sesi offline dan online
    # 2 SKS = hanya sesi offline
    # Mode sudah ditentukan di JSON (field "mode")
    if reguler in REG_AB:
        return item.get("mode", "🏫 Tatap Muka")

    # Reguler CK/CS: berbasis periode, dibalik setelah UTS.
    if reguler in REG_CK_CS and data is not None:

        # Tentukan periode saat ini berdasarkan tanggal UTS dan UAS
        sekarang = datetime.now(WIB)
        uts_date = datetime.strptime(data.get("uts_date", "2026-05-15"), "%Y-%m-%d").replace(tzinfo=WIB)
        uas_date = datetime.strptime(data.get("uas_date", "2026-07-04"), "%Y-%m-%d").replace(tzinfo=WIB)

        periode_saat_ini = 1 if sekarang < uts_date else 2

        # Periode di JSON
        periode_json = item.get("periode", 1)

        # Logika:
        # Periode 1 (sebelum UTS) + Periode JSON 1 = Offline
        # Periode 2 (setelah UTS) + Periode JSON 1 = Online
        # Periode 1 (sebelum UTS) + Periode JSON 2 = Online
        # Periode 2 (setelah UTS) + Periode JSON 2 = Offline
        if periode_json == 1:
            return "🏫 Tatap Muka" if periode_saat_ini == 1 else "💻 Online"
        else:  # periode_json == 2
            return "💻 Online" if periode_saat_ini == 1 else "🏫 Tatap Muka"

    # Fallback untuk kelas lain: pola lama ganjil/genap.
    periode = item.get("periode", 1)
    if minggu_ke % 2 == 0:
        if periode == 1:
            return "💻 Online"
        return "🏫 Tatap Muka"

    if periode == 1:
        return "🏫 Tatap Muka"

    return "💻 Online"
    
def get_week_number(
    semester_mulai,
    target_date
):

    return (
        (target_date - semester_mulai).days // 7
    ) + 1

def get_global_week(data):

    sekarang = datetime.now(WIB)

    semester_mulai = datetime.strptime(
        data["semester_mulai"],
        "%Y-%m-%d"
    ).replace(tzinfo=WIB)

    minggu_ke = (
        (sekarang - semester_mulai).days // 7
    ) + 1

    return max(minggu_ke, 1)

def enrich_data(data):

    minggu_ke = get_global_week(data)
    reguler = str(data.get("reguler", "")).strip().upper()

    for item in data["jadwal"]:

        # Untuk REG_AB, konversi mode dari JSON (offline/online) ke format dengan emoji
        # Untuk REG_CK_CS, mode ditentukan oleh fungsi get_mode berdasarkan periode
        if reguler in REG_AB:
            json_mode = item.get("mode", "offline")
            if json_mode == "offline":
                item["mode"] = "🏫 Tatap Muka"
            elif json_mode == "online":
                item["mode"] = "💻 Online"
            else:
                item["mode"] = "🏫 Tatap Muka"
        else:
            # Untuk REG_CK_CS dan lainnya, gunakan fungsi get_mode
            item["mode"] = get_mode(
                item,
                minggu_ke,
                reguler,
                data
            )

    return data

# ==========================
# NEXT CLASS
# ==========================


def get_schedule_slots(data):

    slots = {}

    for item in data["jadwal"]:

        key = (
            item["hari"],
            item["jam_mulai"],
            item["jam_selesai"]
        )

        if key not in slots:
            slots[key] = {
                "items": [],
                "hari": item["hari"],
                "jam_mulai": item["jam_mulai"],
                "jam_selesai": item["jam_selesai"]
            }

        slots[key]["items"].append(item)

    return list(slots.values())


def get_active_slot_keys(data):

    sekarang = datetime.now(WIB)

    today_name = list(HARI_MAP.keys())[sekarang.weekday()]

    grace_period = timedelta(minutes=5)

    active_keys = set()

    for slot in get_schedule_slots(data):

        if slot["hari"] != today_name:
            continue

        mulai = datetime.strptime(
            slot["jam_mulai"],
            "%H:%M"
        ).replace(
            year=sekarang.year,
            month=sekarang.month,
            day=sekarang.day,
            tzinfo=WIB
        )

        selesai = datetime.strptime(
            slot["jam_selesai"],
            "%H:%M"
        ).replace(
            year=sekarang.year,
            month=sekarang.month,
            day=sekarang.day,
            tzinfo=WIB
        )

        if (mulai - grace_period) <= sekarang <= selesai:
            active_keys.add((slot["hari"], slot["jam_mulai"], slot["jam_selesai"]))

    return active_keys

def get_next_class(data):

    sekarang = datetime.now(WIB)

    slots = get_schedule_slots(data)
    active_slot_keys = get_active_slot_keys(data)

    # Cari hari berikutnya yang memiliki jadwal
    hari_berikutnya = None
    min_selisih_hari = 8  # Lebih dari 7 hari

    for slot in slots:

        slot_key = (slot["hari"], slot["jam_mulai"], slot["jam_selesai"])

        if slot_key in active_slot_keys:
            continue

        hari = slot["hari"]
        selisih_hari = (HARI_MAP[hari] - sekarang.weekday()) % 7

        if selisih_hari == 0:
            # Hari ini, cek apakah jamnya sudah lewat
            jam, menit = map(int, slot["jam_mulai"].split(":"))
            target = sekarang.replace(
                hour=jam,
                minute=menit,
                second=0,
                microsecond=0
            )
            if target <= sekarang:
                # Sudah lewat, skip
                continue
            else:
                # Masih hari ini
                hari_berikutnya = hari
                min_selisih_hari = 0
                break
        elif selisih_hari < min_selisih_hari:
            hari_berikutnya = hari
            min_selisih_hari = selisih_hari

    # Jika tidak ada hari berikutnya (semua jadwal sudah lewat hari ini), cari hari Senin minggu depan
    if hari_berikutnya is None:
        hari_berikutnya = "Senin"
        min_selisih_hari = (HARI_MAP["Senin"] - sekarang.weekday()) % 7
        if min_selisih_hari == 0:
            min_selisih_hari = 7

    # Ambil semua kelas pada hari berikutnya
    hasil = []

    for slot in slots:

        if slot["hari"] != hari_berikutnya:
            continue

        slot_key = (slot["hari"], slot["jam_mulai"], slot["jam_selesai"])

        if slot_key in active_slot_keys:
            continue

        jam, menit = map(int, slot["jam_mulai"].split(":"))

        target = sekarang.replace(
            hour=jam,
            minute=menit,
            second=0,
            microsecond=0
        ) + timedelta(days=min_selisih_hari)

        items = slot["items"]

        for item in items:
            item["countdown"] = int(
                (target - sekarang).total_seconds()
            )
            hasil.append(item)

    hasil.sort(key=lambda item: item["countdown"])

    # Batasi maksimal 6 mata kuliah
    return hasil[:8]
# ==========================
# CURRENT CLASS
# ==========================

def get_current_class(data):

    sekarang = datetime.now(WIB)

    today_name = list(HARI_MAP.keys())[sekarang.weekday()]

    grace_period = timedelta(minutes=5)

    current_slots = []

    for slot in get_schedule_slots(data):

        if slot["hari"] != today_name:
            continue

        mulai = datetime.strptime(
            slot["jam_mulai"],
            "%H:%M"
        ).replace(
            year=sekarang.year,
            month=sekarang.month,
            day=sekarang.day,
            tzinfo=WIB
        )

        selesai = datetime.strptime(
            slot["jam_selesai"],
            "%H:%M"
        ).replace(
            year=sekarang.year,
            month=sekarang.month,
            day=sekarang.day,
            tzinfo=WIB
        )

        if (mulai - grace_period) <= sekarang <= selesai:
            countdown = int((selesai - sekarang).total_seconds())

            for item in slot["items"]:
                item["countdown"] = countdown

            current_slots.extend(slot["items"])

    return current_slots


# ==========================
# INFO AKADEMIK
# ==========================

def get_week_info(data):

    sekarang = datetime.now(WIB)

    semester_mulai = datetime.strptime(
        data["semester_mulai"],
        "%Y-%m-%d"
    ).replace(tzinfo=WIB)

    minggu_ke = (
        (sekarang - semester_mulai).days
        // 7
    ) + 1
    minggu_ke = max(minggu_ke, 1)

    reguler = str(data.get("reguler", "")).strip().upper()

    if reguler in REG_AB:
        # Reg A/B: mode ditentukan oleh SKS, bukan minggu ganjil/genap
        return {
            "minggu_ke": minggu_ke,
            "mode_akademik": "Sistem SKS",
            "keterangan": f"Reg {reguler} - Mode berdasarkan SKS"
        }

    if reguler in REG_CK_CS:
        # Tentukan periode saat ini berdasarkan tanggal UTS dan UAS
        uts_date = datetime.strptime(data.get("uts_date", "2026-05-15"), "%Y-%m-%d").replace(tzinfo=WIB)
        uas_date = datetime.strptime(data.get("uas_date", "2026-07-04"), "%Y-%m-%d").replace(tzinfo=WIB)

        periode_saat_ini = 1 if sekarang < uts_date else 2
        fase = "Sebelum UTS" if periode_saat_ini == 1 else "Setelah UTS"
        return {
            "minggu_ke": minggu_ke,
            "mode_akademik": "Sistem Periode",
            "keterangan": (
                f"Reg {reguler} - {fase}, "
                f"Periode Saat Ini: {periode_saat_ini}"
            )
        }

    if minggu_ke % 2 == 0:
        periode_aktif = 1
    else:
        periode_aktif = 2

    return {
        "minggu_ke": minggu_ke,
        "mode_akademik": "Sistem Periode",
        "keterangan": f"Periode Aktif: {periode_aktif}"
    }


# ==========================
# PROGRESS SEMESTER
# ==========================

def get_progress(data):

    sekarang = datetime.now(WIB)

    semester_mulai = datetime.strptime(
        data["semester_mulai"],
        "%Y-%m-%d"
    ).replace(tzinfo=WIB)

    semester_selesai = datetime.strptime(
        data["semester_selesai"],
        "%Y-%m-%d"
    ).replace(tzinfo=WIB)

    total_hari = (semester_selesai - semester_mulai).days
    hari_berlalu = (sekarang - semester_mulai).days

    if hari_berlalu < 0:
        return 0

    persen = round(
        (
            hari_berlalu
            / total_hari
        ) * 100
    )

    return min(
        persen,
        100
    )


# ==========================
# HOME
# ==========================

@app.route("/")
def home():

    classes = get_available_classes()

    jurusan = sorted(
        list(
            set(
                c["jurusan"]
                for c in classes
            )
        )
    )

    semester = sorted(
        list(
            set(
                c["semester"]
                for c in classes
            )
        )
    )

    return render_template(
        "home.html",
        jurusan=jurusan,
        semester=semester,
        classes=classes
    )


# ==========================
# AJAX CLASS
# ==========================

@app.route("/get_classes")
def get_classes():

    jurusan = request.args.get(
        "jurusan"
    )

    semester = request.args.get(
        "semester"
    )

    hasil = []

    for item in get_available_classes():

        if (
            item["jurusan"] == jurusan
            and
            item["semester"] == semester
        ):

            hasil.append(
                item["kelas"]
            )

    return {
        "classes": hasil
    }


# ==========================
# OPEN SCHEDULE
# ==========================

@app.route(
    "/open",
    methods=["POST"]
)
def open_schedule():

    jurusan = request.form[
        "jurusan"
    ]

    semester = request.form[
        "semester"
    ]

    kelas = request.form[
        "kelas"
    ]

    return redirect(
        f"/jadwal/"
        f"{jurusan}/"
        f"{semester}/"
        f"{kelas}"
    )


# ==========================
# SCHEDULE PAGE
# ==========================

@app.route(
    "/jadwal/<jurusan>/<semester>/<kelas>"
)
def jadwal(
    jurusan,
    semester,
    kelas
):

    data = load_data(
        jurusan,
        semester,
        kelas
    )

    data = enrich_data(data)

    next_class = get_next_class(data)

    current_class = get_current_class(data)

    week_info = get_week_info(data)

    progress = get_progress(data)

    return render_template(
        "schedule.html",
        jadwal=data["jadwal"],
        next_class=next_class,
        current_class=current_class,
        minggu_ke=week_info["minggu_ke"],
        mode_akademik=week_info["mode_akademik"],
        keterangan_akademik=week_info["keterangan"],
        progress=progress,
        jurusan=jurusan,
        semester=semester,
        kelas=kelas
    )

# ==========================
# MAIN
# ==========================

if __name__ == "__main__":

    app.run(
        debug=True
    )
