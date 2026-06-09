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
    reguler
):

    periode = item.get("periode")

    # Reguler A/B: pola ganjil/genap.
    # Minggu ganjil (1,3,5,7,9,11,13,15): matkul dengan elearning=true menjadi Online, lainnya Tatap Muka.
    # Minggu genap (2,4,6,8,10,12,14,16): semua matkul Tatap Muka.
    if reguler in REG_AB:

        if (
            minggu_ke % 2 == 1  # Minggu ganjil
            and
            item.get("elearning", False) is True
        ):
            return "💻 Online"

        return "🏫 Tatap Muka"

    # Reguler CK/CS: berbasis periode, dibalik setelah UTS.
    if reguler in REG_CK_CS:

        sebelum_uts = minggu_ke <= 8

        if periode == 1:
            return "🏫 Tatap Muka" if sebelum_uts else "💻 Online"

        if periode == 2:
            return "💻 Online" if sebelum_uts else "🏫 Tatap Muka"

    # Fallback untuk kelas lain: pola lama ganjil/genap.
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

        item["mode"] = get_mode(
            item,
            minggu_ke,
            reguler
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
            item["mulai"],
            item["selesai"]
        )

        if key not in slots:
            slots[key] = {
                "items": [],
                "hari": item["hari"],
                "mulai": item["mulai"],
                "selesai": item["selesai"]
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
            slot["mulai"],
            "%H:%M"
        ).replace(
            year=sekarang.year,
            month=sekarang.month,
            day=sekarang.day,
            tzinfo=WIB
        )

        selesai = datetime.strptime(
            slot["selesai"],
            "%H:%M"
        ).replace(
            year=sekarang.year,
            month=sekarang.month,
            day=sekarang.day,
            tzinfo=WIB
        )

        if (mulai - grace_period) <= sekarang <= selesai:
            active_keys.add((slot["hari"], slot["mulai"], slot["selesai"]))

    return active_keys

def get_next_class(data):

    sekarang = datetime.now(WIB)

    slots = get_schedule_slots(data)
    active_slot_keys = get_active_slot_keys(data)

    kandidat = {
        "💻 Online": None,
        "🏫 Tatap Muka": None,
    }

    for slot in slots:

        slot_key = (slot["hari"], slot["mulai"], slot["selesai"])

        if slot_key in active_slot_keys:
            continue

        hari = slot["hari"]
        jam, menit = map(int, slot["mulai"].split(":"))

        selisih_hari = (HARI_MAP[hari] - sekarang.weekday()) % 7

        target = sekarang.replace(
            hour=jam,
            minute=menit,
            second=0,
            microsecond=0
        ) + timedelta(days=selisih_hari)

        if target <= sekarang:
            target += timedelta(days=7)

        items = slot["items"]

        for item in items:
            item["countdown"] = int(
                (target - sekarang).total_seconds()
            )

            mode = item.get("mode")

            if mode not in kandidat:
                continue

            if kandidat[mode] is None or target < kandidat[mode][0]:
                kandidat[mode] = (target, item)

    hasil = []

    for mode in ("💻 Online", "🏫 Tatap Muka"):

        if kandidat[mode] is not None:
            hasil.append(kandidat[mode][1])

    hasil.sort(key=lambda item: item["countdown"])

    return hasil
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
            slot["mulai"],
            "%H:%M"
        ).replace(
            year=sekarang.year,
            month=sekarang.month,
            day=sekarang.day,
            tzinfo=WIB
        )

        selesai = datetime.strptime(
            slot["selesai"],
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
        tipe_minggu = "Ganjil" if minggu_ke % 2 == 1 else "Genap"
        return {
            "minggu_ke": minggu_ke,
            "mode_akademik": "Siklus Mingguan",
            "keterangan": f"Reg {reguler} - Minggu {tipe_minggu}"
        }

    if reguler in REG_CK_CS:
        sebelum_uts = minggu_ke <= 8
        periode_tatap_muka = 1 if sebelum_uts else 2
        fase = "Sebelum UTS" if sebelum_uts else "Setelah UTS"
        return {
            "minggu_ke": minggu_ke,
            "mode_akademik": "Sistem Periode",
            "keterangan": (
                f"Reg {reguler} - {fase}, "
                f"Periode Tatap Muka: {periode_tatap_muka}"
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

    total_minggu = 16

    minggu_ke = (
        (sekarang - semester_mulai).days
        // 7
    ) + 1

    persen = round(
        (
            minggu_ke
            / total_minggu
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
