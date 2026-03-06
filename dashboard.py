import sqlite3
from pathlib import Path
from flask import Flask, render_template

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "cell_counts.db"
POPS = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]

app = Flask(__name__)


@app.route("/")
def index():
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
    return render_template("dashboard.html", rows=data)


if __name__ == "__main__":
    app.run()
