import base64
import io
import sqlite3
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu
from flask import Flask, render_template

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "cell_counts.db"
POPS = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/part2")
def part2():
    data = []
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte FROM samples ORDER BY id")
    for row in cur:
        counts = [row[i] for i in range(1, 6)]
        total = sum(counts)
        if total == 0:
            continue
        for pop, c in zip(POPS, counts):
            data.append({"sample": row[0], "total_count": total, "population": pop, "count": c, "percentage": (c / total) * 100})
    conn.close()
    return render_template("part2.html", rows=data)


@app.route("/part3")
def part3():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT sub.response, s.b_cell, s.cd8_t_cell, s.cd4_t_cell, s.nk_cell, s.monocyte
        FROM samples s JOIN subjects sub ON s.subject_id = sub.id
        WHERE sub.condition='melanoma' AND sub.treatment='miraclib'
          AND sub.response IN ('yes','no') AND s.sample_type='PBMC'
    """)
    by_pop = {p: {"yes": [], "no": []} for p in POPS}
    for r in cur:
        resp, counts = r[0], list(r[1:6])
        total = sum(counts)
        if total == 0:
            continue
        for i, p in enumerate(POPS):
            by_pop[p][resp].append((counts[i] / total) * 100)
    conn.close()
    stats = []
    for p in POPS:
        yes, no = by_pop[p]["yes"], by_pop[p]["no"]
        if len(yes) < 2 or len(no) < 2:
            stats.append({"pop": p, "n_yes": len(yes), "n_no": len(no), "p": None, "sig": False})
            continue
        _, pval = mannwhitneyu(yes, no, alternative="two-sided")
        stats.append({"pop": p, "n_yes": len(yes), "n_no": len(no), "p": pval, "sig": pval < 0.05})

    fig, axes = plt.subplots(2, 3, figsize=(10, 6))
    for i, p in enumerate(POPS):
        ax = axes.flatten()[i]
        ax.boxplot([by_pop[p]["yes"], by_pop[p]["no"]], labels=["Responders", "Non-responders"])
        ax.set_ylabel("%")
        ax.set_title(p)
    axes.flatten()[5].axis("off")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120)
    plt.close()
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode()
    return render_template("part3.html", stats=stats, plot_b64=img_b64)


@app.route("/part4")
def part4():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    base = """
        FROM samples s JOIN subjects sub ON s.subject_id = sub.id
        WHERE sub.condition='melanoma' AND sub.treatment='miraclib'
          AND s.sample_type='PBMC' AND s.time_from_treatment_start=0
    """
    cur.execute("SELECT sub.project_id, COUNT(*)" + base + " GROUP BY sub.project_id")
    by_project = [{"project": r[0], "n_samples": r[1]} for r in cur]
    cur.execute("SELECT sub.response, COUNT(DISTINCT s.subject_id)" + base + " GROUP BY sub.response")
    by_response = [{"response": r[0], "n_subjects": r[1]} for r in cur]
    cur.execute("SELECT sub.sex, COUNT(DISTINCT s.subject_id)" + base + " GROUP BY sub.sex")
    by_sex = [{"sex": r[0], "n_subjects": r[1]} for r in cur]
    cur.execute("SELECT s.id, s.subject_id, sub.project_id, sub.response, sub.sex" + base + " ORDER BY sub.project_id, s.id")
    rows = [{"sample": r[0], "subject": r[1], "project": r[2], "response": r[3] or "", "sex": r[4]} for r in cur]
    conn.close()
    return render_template("part4.html", by_project=by_project, by_response=by_response, by_sex=by_sex, rows=rows)


if __name__ == "__main__":
    app.run(debug=True)
