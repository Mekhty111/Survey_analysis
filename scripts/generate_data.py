"""Generates ~80 realistic mock responses for the procrastination survey (survey/sorgu.md).

Each respondent gets a hidden "procrastination tendency" z ~ N(0,1). Answers are drawn
from distributions conditioned on z (plus noise), so the data has believable correlations
instead of pure randomness. Fixed seed -> reproducible dataset.
"""
import csv
import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(2026)
N = 82
ROOT = Path(__file__).resolve().parent.parent


def sig(x):
    return 1 / (1 + math.exp(-x))


def clip(v, lo, hi):
    return max(lo, min(hi, v))


def pick(options, weights):
    return random.choices(options, weights=weights, k=1)[0]


def half(x):
    return round(x * 2) / 2


AGES = ["17–18", "19–20", "21–22", "23 və yuxarı"]
GENDERS = ["Qadın", "Kişi", "Demək istəmirəm"]
YEARS = ["1-ci kurs", "2-ci kurs", "3-cü kurs", "4-cü kurs", "Magistratura"]
FIELDS = ["Riyaziyyat və İT", "Təbiət elmləri", "Hüquq",
          "Beynəlxalq münasibətlər və iqtisadiyyat", "Filologiya və jurnalistika",
          "Sosial elmlər və psixologiya"]
HOUSING = ["Ailə ilə", "Yataqxanada", "Kirayə evdə"]
WORK = ["Xeyr", "Bəli, yarımştat / frilans", "Bəli, tam ştat"]
START = ["Tapşırıq veriləndən dərhal sonra", "Dedlayndan bir neçə gün əvvəl",
         "Dedlayndan bir gün əvvəl", "Dedlayn günü, son saatlarda",
         "Dedlayndan sonra (gecikdirirəm)"]
ALLNIGHT = ["Heç vaxt", "1–2 dəfə", "3–5 dəfə", "6 və daha çox"]
TASKS = ["Esse / kurs işi yazmaq", "İmtahana hazırlaşmaq", "Mühazirə materiallarını oxumaq",
         "Qrup layihəsi", "Laboratoriya / praktiki tapşırıq"]
REASONS = ["Motivasiyam yoxdur", "Mövzu darıxdırıcıdır", "Nədən başlayacağımı bilmirəm",
           "Mükəmməl etmək istəyirəm, ona görə başlamıram", "Yorğunluq",
           "Stres altında daha yaxşı işləyirəm"]
CHRONO = ["Səhər", "Gündüz", "Axşam", "Gecə"]
GPA_BINS = ["51–60", "61–70", "71–80", "81–90", "91–100"]

ADVICE = [
    "telefonu basqa otaga qoymaq cox kmek edir",
    "Tapşırığı kiçik hissələrə bölmək işləyir, birinci addım 10 dəqiqəlik olanda başlamaq asan olur.",
    "pomodoro yaxsi islyir, 25 deqiqe is 5 deqiqe fasile",
    "Dedlayndan 2 gün əvvəli özünə dedlayn kimi yazanda daha az gecikir insan",
    "evde oxumaq alinmir, kitabxanada daha cox is gorulur )",
    "dostla birlikde oxuyanda bir birine nezaret olur",
    "mukemmel olmasada olar, esas baslamaqdi sonra duzeltmek olur",
    "Yuxu düz olmayanda yorğun beyin hər şeyi təxirə salır.",
    "Səhər ilk iş ən çətin tapşırığı etmək yaxşı nəticə verir",
    "tiktoku silenden sonra vallah ferq hiss olunur",
    "to do list yazib bitirdiklerini xetlemek motivasiya verir",
    "kicik mukafat isleyir, bitirdin - cay sirniyyat )",
    "bilmirem bu hele oyrenilir )))",
    "Notionda plan qurmaq kömək edir",
    "sosial sebekelere limit qoyanda daha az vaxt itir, telefonda bu funksiya var",
    "2 deqiqelik qayda: 2 deqiqeye biten isi derhal etmek lazimdi",
    "sabaha saxlamaq olmaz cunki sabah basqa is cixir onsuzda",
    "en azinan ilk cumleni yazanda qalani ozu gelir",
    "Musiqisiz sakit yerdə oxumaq daha effektivdir",
    "qrup layihesinde islerri ilk gunden bolmek lazimdi yoxsa son gun hamsi bir neferin ustune qalir",
    "gece oxumaq effektiv deyil, yatib seher etmek daha yaxsidi",
    "Özünü günahlandırmaq heç nəyi dəyişmir, sadəcə növbəti addım atılmalıdır",
    "kofee icib baslamaq komek edir )",
    "deadline qorxusu en yaxsi motivasiyadi ))",
    "slam, mence en yaxsisi telefonu sondurmekdi",
    "plan qurmaq isleyirr amma ona emel etmek cetindi )",
    "dedlaynnan qabaq hemise panika olur, sonra hersey birtehr alinir",
    "gunorta yatmaqq olmaz, sonra axsama qeder hecne olmur",
    "kitabxanda oxumaq daha rahatdi, ev seraiti bele deyil",
]

rows = []
advice_rng = random.Random(11)  # separate stream: editing ADVICE must not change the numeric data
new_rng = random.Random(41)     # separate stream for questions 20–23 (added later)
unc_rng = random.Random(29)     # separate stream for "don't know / prefer not to say" answers

# uncertain answer options and how often real respondents tend to pick them
UNCERTAIN = {
    "start_time": ("Bilmirəm, hər dəfə fərqli olur", 0.06),
    "all_nighters": ("Xatırlamıram", 0.06),
    "main_reason": ("Bilmirəm", 0.07),
    "screen_time_h": ("Bilmirəm", 0.09),
    "gpa": ("Demək istəmirəm", 0.08),
}
UNCERTAIN_NEW = {
    "planning": ("Bilmirəm, plan qurmuram", 0.07),
    "ai_last_minute": ("Demək istəmirəm", 0.11),
}

FEELINGS = ["Rahat, heç bir problem görmürəm", "Günahkar", "Narahat, stres hiss edirəm", "Heç nə hiss etmirəm"]
PLANNING = ["Planladığımdan az", "Təxminən planladığım qədər", "Təxminən 1,5 dəfə çox", "2 dəfə və daha çox"]
EXTENSION = ["Əvvəlki plan üzrə davam edirəm və vaxtında bitirirəm", "Əlavə vaxtı işi yaxşılaşdırmağa sərf edirəm",
             "Başlamağı yeni dedlayna yaxın vaxta keçirirəm"]
AI_USE = ["Heç vaxt", "1–2 dəfə", "Tez-tez"]
start_date = datetime(2026, 10, 6, 9, 0)

for i in range(N):
    z = random.gauss(0, 1)

    # BDU, only 2nd and 3rd year bachelor students
    year_i = pick([1, 2], [45, 55])
    age_i = pick(range(4), [8, 70, 20, 2] if year_i == 1 else [0, 30, 62, 8])
    gender = pick(GENDERS, [54, 43, 3])
    field_i = pick(range(6), [22, 16, 15, 17, 16, 14])
    housing = pick(HOUSING, [52, 22, 26])
    work_i = pick(range(3), [62, 32, 6] if year_i == 1 else [50, 40, 10])

    # field / work nudge the tendency a bit
    z += {0: 0.0, 1: -0.25, 2: -0.1, 3: 0.15, 4: 0.25, 5: 0.1}[field_i]
    z += {0: 0.0, 1: 0.1, 2: 0.35}[work_i]

    self_score = int(clip(round(5.6 + 1.9 * z + random.gauss(0, 0.9)), 1, 10))

    start_i = int(clip(round(1.6 + 0.95 * z + random.gauss(0, 0.6)), 0, 4))

    chrono_w = [max(1, 30 - 12 * z), 30, 28 + 4 * z, max(1, 18 + 14 * z)]
    chrono = pick(CHRONO, chrono_w)

    an_score = 0.9 + 0.8 * z + (0.5 if chrono == "Gecə" else 0) + random.gauss(0, 0.6)
    allnight_i = int(clip(round(an_score), 0, 3))

    task = pick(TASKS, [28 + 8 * (field_i in (2, 4, 5)), 26, 22, 12, 6 + 18 * (field_i in (0, 1))])

    reason_w = [22 + 6 * z, 16 + 3 * z, 18, 12 - 3 * z, 14 + 6 * (work_i > 0), 10 + 8 * z]
    reason = pick(REASONS, [max(1, w) for w in reason_w])

    platforms = []
    if random.random() < sig(1.2 + 0.3 * z): platforms.append("Instagram")
    if random.random() < sig(-0.3 + 1.1 * z - 0.6 * (age_i == 3)): platforms.append("TikTok")
    if random.random() < sig(0.1 + 0.4 * z): platforms.append("YouTube")
    if random.random() < sig(-1.3 + 0.4 * z + 1.4 * (gender == "Kişi")): platforms.append("Oyunlar")
    if random.random() < sig(-0.7 + 0.3 * z + 0.4 * (gender == "Qadın")): platforms.append("Seriallar / filmlər")
    if random.random() < sig(-0.2 + 0.2 * z): platforms.append("Mesajlaşma (WhatsApp, Telegram)")
    if random.random() < sig(-1.5 + 0.4 * z + 0.6 * (work_i > 0)): platforms.append("Yatmaq")
    if random.random() < sig(-1.2 + 0.2 * z + 0.4 * (housing == "Yataqxanada")): platforms.append("Dostlarla vaxt keçirmək")
    if not platforms:
        platforms.append("Instagram")

    screen = half(clip(4.7 + 1.0 * z + 0.8 * ("TikTok" in platforms) + random.gauss(0, 1.6), 1.5, 11))

    sleep = half(clip(7.0 - 0.45 * z - 0.6 * (chrono == "Gecə") - 0.4 * (work_i > 0)
                      - 0.2 * allnight_i + random.gauss(0, 0.8), 4, 9.5))

    coping = []
    if random.random() < sig(-1.3 - 0.8 * z): coping.append("Pomodoro texnikası")
    if random.random() < sig(-0.1 - 0.7 * z): coping.append("To-do siyahısı / planlayıcı")
    if random.random() < sig(-1.2 - 0.3 * z): coping.append("Telefonu söndürmək və ya uzaqda saxlamaq")
    if random.random() < sig(-1.0 - 0.3 * z + 0.6 * (housing != "Ailə ilə")): coping.append("Kitabxanada oxumaq")
    if random.random() < sig(-1.3): coping.append("Dostla birlikdə oxumaq")
    if not coping or random.random() < sig(-2.6 + 1.2 * z):
        coping = ["Heç nə"]

    stress = int(clip(round(3.0 + 0.6 * z + 0.6 * (reason.startswith("Mükəmməl")) + random.gauss(0, 0.7)), 1, 5))
    impact = int(clip(round(3.1 + 0.55 * z + random.gauss(0, 0.8)), 1, 5))

    # GPA: procrastination hurts, "stress helps me" belief does not
    gpa = (78 - 5.2 * z + {0: 0, 1: 0, 2: -1, 3: 1, 4: 1.5, 5: 1}[field_i]
           + 2.5 * ("Pomodoro texnikası" in coping) + 1.5 * ("To-do siyahısı / planlayıcı" in coping)
           + 0.8 * (sleep - 7) + 2.0 * (reason.startswith("Mükəmməl")) + random.gauss(0, 6.5))
    gpa = clip(gpa, 52, 99)
    gpa_bin = GPA_BINS[min(4, int((gpa - 51) // 10))]

    # questions 20–23: drawn from their own random stream so the earlier answers stay identical
    feeling = new_rng.choices(FEELINGS, weights=[max(2, 26 - 9 * z), max(4, 26 + 9 * z),
                                                 max(4, 30 + 5 * z), 14 + 3 * abs(z)])[0]
    plan_i = int(clip(round(1.55 + 0.75 * z + 0.25 * (start_i - 2) + new_rng.gauss(0, 0.65)), 0, 3))
    ext_w = [max(3, 38 - 16 * z), max(3, 28 - 6 * z), max(4, 30 + 20 * z)]
    extension = new_rng.choices(EXTENSION, weights=ext_w)[0]
    ai_i = int(clip(round(0.75 + 0.7 * z + 0.3 * (start_i >= 3) + new_rng.gauss(0, 0.8)), 0, 2))

    advice = ""
    if random.random() < 0.42:
        random.randrange(24)  # keep the main random stream identical to the published dataset
        advice = advice_rng.choice(ADVICE)

    ts = start_date + timedelta(minutes=int(random.expovariate(1 / 260)) * (1 + i // 8) + i * 170)

    row = {
        "id": f"R{i + 1:03d}",
        "timestamp": ts.strftime("%Y-%m-%d %H:%M"),
        "age": AGES[age_i],
        "gender": gender,
        "year": YEARS[year_i],
        "field": FIELDS[field_i],
        "housing": housing,
        "work": WORK[work_i],
        "self_score": self_score,
        "start_time": START[start_i],
        "all_nighters": ALLNIGHT[allnight_i],
        "most_delayed_task": task,
        "main_reason": reason,
        "time_thieves": "; ".join(platforms),
        "screen_time_h": screen,
        "productive_time": chrono,
        "sleep_h": sleep,
        "coping": "; ".join(coping),
        "stress_1_5": stress,
        "hurts_grades_1_5": impact,
        "gpa": gpa_bin,
        "feeling": feeling,
        "planning": PLANNING[plan_i],
        "deadline_extension": extension,
        "ai_last_minute": AI_USE[ai_i],
        "advice": advice,
    }
    for key, (label, prob) in UNCERTAIN.items():
        if unc_rng.random() < prob:
            row[key] = label
    for key, (label, prob) in UNCERTAIN_NEW.items():
        if new_rng.random() < prob:
            row[key] = label
    rows.append(row)

rows.sort(key=lambda r: r["timestamp"])
for k, r in enumerate(rows):
    r["id"] = f"R{k + 1:03d}"

(ROOT / "data").mkdir(exist_ok=True)
with open(ROOT / "data" / "responses.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
with open(ROOT / "data" / "responses.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=1)

print(f"Wrote {len(rows)} responses")
