"""Reads data/responses.json, computes aggregates and cross-tabs, writes site/data.js."""
import json
import statistics as st
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = json.load(open(ROOT / "data" / "responses.json", encoding="utf-8"))
N = len(R)

AGES = ["17–18", "19–20", "21–22", "23 və yuxarı"]
YEARS = ["2-ci kurs", "3-cü kurs"]
START = ["Tapşırıq veriləndən dərhal sonra", "Dedlayndan bir neçə gün əvvəl",
         "Dedlayndan bir gün əvvəl", "Dedlayn günü, son saatlarda",
         "Dedlayndan sonra (gecikdirirəm)"]
ALLNIGHT = ["Heç vaxt", "1–2 dəfə", "3–5 dəfə", "6 və daha çox"]
CHRONO = ["Səhər", "Gündüz", "Axşam", "Gecə"]
GPA = ["51–60", "61–70", "71–80", "81–90", "91–100"]
GPA_MID = {"51–60": 55.5, "61–70": 65.5, "71–80": 75.5, "81–90": 85.5, "91–100": 95.5}
WORK = ["Xeyr", "Bəli, yarımştat / frilans", "Bəli, tam ştat"]

# "don't know / prefer not to say" answers: shown as their own (gray) bin, excluded from calculations
FEELINGS = ["Rahat, heç bir problem görmürəm", "Günahkar", "Narahat, stres hiss edirəm", "Heç nə hiss etmirəm"]
PLANNING = ["Planladığımdan az", "Təxminən planladığım qədər", "Təxminən 1,5 dəfə çox", "2 dəfə və daha çox"]
EXTENSION = ["Əvvəlki plan üzrə davam edirəm və vaxtında bitirirəm", "Əlavə vaxtı işi yaxşılaşdırmağa sərf edirəm",
             "Başlamağı yeni dedlayna yaxın vaxta keçirirəm"]
AI_USE = ["Heç vaxt", "1–2 dəfə", "Tez-tez"]
U_PLAN, U_AI = "Bilmirəm, plan qurmuram", "Demək istəmirəm"
U_START, U_ALLNIGHT, U_REASON, U_SCREEN, U_GPA = (
    "Bilmirəm, hər dəfə fərqli olur", "Xatırlamıram", "Bilmirəm", "Bilmirəm", "Demək istəmirəm")
UNCERTAIN = sorted({U_START, U_ALLNIGHT, U_REASON, U_SCREEN, U_GPA, U_PLAN, U_AI, "Demək istəmirəm"})


def split(v):
    return [x for x in v.split("; ") if x]


def dist(key, order=None, multi=False):
    c = Counter()
    for r in R:
        for v in (split(r[key]) if multi else [r[key]]):
            c[v] += 1
    keys = order or [k for k, _ in c.most_common()]
    keys = [k for k in keys if k not in UNCERTAIN] + [k for k in keys if k in UNCERTAIN]
    return {"labels": keys, "counts": [c.get(k, 0) for k in keys]}


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(st.mean(xs), 2) if xs else None


def group_mean(key, val, order=None, multi=False, min_n=1):
    groups = {}
    for r in R:
        for g in (split(r[key]) if multi else [r[key]]):
            v = val(r)
            if v is not None:
                groups.setdefault(g, []).append(v)
    keys = order or sorted(groups, key=lambda g: -st.mean(groups[g]))
    keys = [k for k in keys if len(groups.get(k, [])) >= min_n]
    keys = [k for k in keys if k not in UNCERTAIN] + [k for k in keys if k in UNCERTAIN]
    return {"labels": keys, "means": [mean(groups[k]) for k in keys], "n": [len(groups[k]) for k in keys]}


def pearson(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    xs, ys = [p[0] for p in pairs], [p[1] for p in pairs]
    mx, my = st.mean(xs), st.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
    return round(num / den, 2)


gpa = lambda r: GPA_MID.get(r["gpa"])
screen = lambda r: r["screen_time_h"] if isinstance(r["screen_time_h"], (int, float)) else None
score = lambda r: r["self_score"]

late = [r for r in R if r["start_time"] in START[3:]]
high = [r for r in R if r["self_score"] >= 7]
low = [r for r in R if r["self_score"] <= 4]
tiktok = [r for r in R if "TikTok" in split(r["time_thieves"])]
no_tiktok = [r for r in R if "TikTok" not in split(r["time_thieves"])]
pomodoro = [r for r in R if "Pomodoro texnikası" in split(r["coping"])]
nothing = [r for r in R if r["coping"] == "Heç nə"]
stress_believers = [r for r in R if r["main_reason"] == "Stres altında daha yaxşı işləyirəm"]
night = [r for r in R if r["productive_time"] == "Gecə"]
morning = [r for r in R if r["productive_time"] == "Səhər"]
allnighters = [r for r in R if r["all_nighters"] in ALLNIGHT[1:]]
self_aware = [r for r in R if r["hurts_grades_1_5"] >= 4]

# scatter: screen time vs self score
scatter = [{"x": screen(r), "y": r["self_score"]} for r in R if screen(r) is not None]

# coping effectiveness: mean self score & gpa by coping method
coping_score = group_mean("coping", score, multi=True)
coping_gpa = group_mean("coping", gpa, order=coping_score["labels"], multi=True)

# start time vs gpa
start_gpa = group_mean("start_time", gpa, order=START + [U_START])
chrono_score = group_mean("productive_time", score, order=CHRONO)
chrono_sleep = group_mean("productive_time", lambda r: r["sleep_h"], order=CHRONO)
reason_gpa = group_mean("main_reason", gpa)
work_score = group_mean("work", score, order=WORK)
field_score = group_mean("field", score)
allnight_sleep = group_mean("all_nighters", lambda r: r["sleep_h"], order=ALLNIGHT + [U_ALLNIGHT])
allnight_gpa = group_mean("all_nighters", gpa, order=ALLNIGHT + [U_ALLNIGHT])
thief_score = group_mean("time_thieves", score, multi=True)

# heatmap: self-score buckets x gpa
buckets = [("1–3", 1, 3), ("4–6", 4, 6), ("7–10", 7, 10)]
heat = []
for name, lo, hi in buckets:
    grp = [r for r in R if lo <= r["self_score"] <= hi and r["gpa"] in GPA_MID]
    c = Counter(r["gpa"] for r in grp)
    heat.append({"bucket": name, "n": len(grp),
                 "pct": [round(100 * c.get(g, 0) / len(grp)) for g in GPA]})

pct = lambda part, whole=N: round(100 * len(part) / whole)


def crosstab(groups, key, cats):
    """groups: list of (name, rows). Returns % of each answer within each group (uncertain answers excluded)."""
    rows_out = []
    for name, grp in groups:
        known = [r for r in grp if r[key] in cats]
        c = Counter(r[key] for r in known)
        rows_out.append({"group": name, "n": len(known),
                         "pct": [round(100 * c.get(k, 0) / len(known)) if known else 0 for k in cats]})
    return {"cats": cats, "rows": rows_out}


score_groups = [(name, [r for r in R if lo <= r["self_score"] <= hi]) for name, lo, hi in buckets]
start_groups = [("Erkən başlayanlar", [r for r in R if r["start_time"] in START[:2]]),
                ("Bir gün əvvəl", [r for r in R if r["start_time"] == START[2]]),
                ("Son anda və ya gec", [r for r in R if r["start_time"] in START[3:]])]
feeling_x = crosstab(score_groups, "feeling", FEELINGS)
planning_x = crosstab(start_groups, "planning", PLANNING)
extension_x = crosstab(score_groups, "deadline_extension", EXTENSION)
ai_x = crosstab(score_groups, "ai_last_minute", AI_USE)
ai_gpa = group_mean("ai_last_minute", gpa, order=AI_USE + [U_AI])
extension_gpa = group_mean("deadline_extension", gpa, order=EXTENSION)
plan_known = [r for r in R if r["planning"] in PLANNING]
underestimate = [r for r in plan_known if r["planning"] in PLANNING[2:]]
ai_known = [r for r in R if r["ai_last_minute"] in AI_USE]

ts = sorted(r["timestamp"] for r in R)

out = {
    "n": N,
    "uncertain_labels": UNCERTAIN,
    "unknown": {
        "start": sum(r["start_time"] == U_START for r in R),
        "allnight": sum(r["all_nighters"] == U_ALLNIGHT for r in R),
        "reason": sum(r["main_reason"] == U_REASON for r in R),
        "screen": sum(screen(r) is None for r in R),
        "gpa": sum(r["gpa"] not in GPA_MID for r in R),
        "planning": sum(r["planning"] == U_PLAN for r in R),
        "ai": sum(r["ai_last_minute"] == U_AI for r in R),
    },
    "period": [ts[0][:10], ts[-1][:10]],
    "kpi": {
        "avg_score": mean(score(r) for r in R),
        "late_pct": pct(late),
        "allnighter_pct": pct(allnighters),
        "avg_screen": mean(screen(r) for r in R),
        "avg_sleep": mean(r["sleep_h"] for r in R),
        "short_sleep_pct": pct([r for r in R if r["sleep_h"] < 7]),
        "self_aware_pct": pct(self_aware),
    },
    "insight": {
        "corr_screen_score": pearson([screen(r) for r in R], [score(r) for r in R]),
        "corr_score_gpa": pearson([score(r) for r in R], [gpa(r) for r in R]),
        "corr_sleep_score": pearson([r["sleep_h"] for r in R], [score(r) for r in R]),
        "tiktok_score": mean(score(r) for r in tiktok),
        "no_tiktok_score": mean(score(r) for r in no_tiktok),
        "tiktok_screen": mean(screen(r) for r in tiktok),
        "no_tiktok_screen": mean(screen(r) for r in no_tiktok),
        "tiktok_n": len(tiktok),
        "pomodoro_score": mean(score(r) for r in pomodoro),
        "pomodoro_gpa": mean(gpa(r) for r in pomodoro),
        "pomodoro_n": len(pomodoro),
        "nothing_score": mean(score(r) for r in nothing),
        "nothing_gpa": mean(gpa(r) for r in nothing),
        "nothing_n": len(nothing),
        "stress_believers_n": len(stress_believers),
        "stress_believers_gpa": mean(gpa(r) for r in stress_believers),
        "stress_believers_score": mean(score(r) for r in stress_believers),
        "all_gpa": mean(gpa(r) for r in R),
        "night_n": len(night), "night_score": mean(score(r) for r in night),
        "night_sleep": mean(r["sleep_h"] for r in night),
        "morning_n": len(morning), "morning_score": mean(score(r) for r in morning),
        "morning_sleep": mean(r["sleep_h"] for r in morning),
        "high_gpa": mean(gpa(r) for r in high), "high_n": len(high),
        "low_gpa": mean(gpa(r) for r in low), "low_n": len(low),
        "high_top_gpa_pct": pct([r for r in high if r["gpa"] in ("81–90", "91–100")], len(high)),
        "low_top_gpa_pct": pct([r for r in low if r["gpa"] in ("81–90", "91–100")], len(low)),
        "late_but_aware_pct": pct([r for r in late if r["hurts_grades_1_5"] >= 4], len(late)),
        "late_n": len(late),
        "underestimate_pct": pct(underestimate, len(plan_known)),
        "plan_known_n": len(plan_known),
        "extension_delay_pct": pct([r for r in R if r["deadline_extension"] == EXTENSION[2]]),
        "extension_improve_pct": pct([r for r in R if r["deadline_extension"] == EXTENSION[1]]),
        "ai_any_pct": pct([r for r in ai_known if r["ai_last_minute"] != "Heç vaxt"], len(ai_known)),
        "ai_known_n": len(ai_known),
        "guilty_or_anxious_high": feeling_x["rows"][2]["pct"][1] + feeling_x["rows"][2]["pct"][2],
        "perfectionist_n": sum(r["main_reason"].startswith("Mükəmməl") for r in R),
        "perfectionist_stress": mean(r["stress_1_5"] for r in R if r["main_reason"].startswith("Mükəmməl")),
        "others_stress": mean(r["stress_1_5"] for r in R if not r["main_reason"].startswith("Mükəmməl")),
    },
    "charts": {
        "age": dist("age", AGES),
        "gender": dist("gender"),
        "year": dist("year", YEARS),
        "field": dist("field"),
        "work": dist("work", WORK),
        "self_score": dist("self_score", list(range(1, 11))),
        "start_time": dist("start_time", START + [U_START]),
        "all_nighters": dist("all_nighters", ALLNIGHT + [U_ALLNIGHT]),
        "task": dist("most_delayed_task"),
        "reason": dist("main_reason"),
        "thieves": dist("time_thieves", multi=True),
        "coping": dist("coping", multi=True),
        "chrono": dist("productive_time", CHRONO),
        "stress": dist("stress_1_5", [1, 2, 3, 4, 5]),
        "hurts": dist("hurts_grades_1_5", [1, 2, 3, 4, 5]),
        "gpa": dist("gpa", GPA + [U_GPA]),
        "scatter": scatter,
        "coping_score": coping_score,
        "coping_gpa": coping_gpa,
        "start_gpa": start_gpa,
        "chrono_score": chrono_score,
        "chrono_sleep": chrono_sleep,
        "reason_gpa": reason_gpa,
        "work_score": work_score,
        "field_score": field_score,
        "allnight_sleep": allnight_sleep,
        "allnight_gpa": allnight_gpa,
        "thief_score": thief_score,
        "heat": {"gpa": GPA, "rows": heat},
        "feeling": dist("feeling", FEELINGS),
        "planning": dist("planning", PLANNING + [U_PLAN]),
        "extension": dist("deadline_extension", EXTENSION),
        "ai": dist("ai_last_minute", AI_USE + [U_AI]),
        "feeling_x": feeling_x,
        "planning_x": planning_x,
        "extension_x": extension_x,
        "ai_x": ai_x,
        "ai_gpa": ai_gpa,
        "extension_gpa": extension_gpa,
    },
    "advice": [r["advice"] for r in R if r["advice"]],
}

(ROOT / "site").mkdir(exist_ok=True)
with open(ROOT / "site" / "data.js", "w", encoding="utf-8") as f:
    f.write("window.SURVEY = ")
    json.dump(out, f, ensure_ascii=False, indent=1)
    f.write(";\n")
print(json.dumps({"kpi": out["kpi"], "insight": out["insight"]}, ensure_ascii=False, indent=1))
for k in ["feeling_x", "planning_x", "extension_x", "ai_x", "ai_gpa", "extension_gpa"]:
    print(k, json.dumps(out["charts"][k], ensure_ascii=False))
for k in ["coping_score", "coping_gpa", "start_gpa", "chrono_score", "reason_gpa", "work_score",
          "field_score", "allnight_gpa", "thief_score"]:
    print(k, json.dumps(out["charts"][k], ensure_ascii=False))
print(json.dumps(out["charts"]["heat"], ensure_ascii=False))
