import sqlite3
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "cell_counts.db"
POPS = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]


def responder_data():
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
    return by_pop


if __name__ == "__main__":
    by_pop = responder_data()
    stats = []
    for p in POPS:
        yes, no = by_pop[p]["yes"], by_pop[p]["no"]
        if len(yes) < 2 or len(no) < 2:
            stats.append({"pop": p, "n_yes": len(yes), "n_no": len(no), "p": None, "sig": False})
            continue
        _, pval = mannwhitneyu(yes, no, alternative="two-sided")
        stats.append({"pop": p, "n_yes": len(yes), "n_no": len(no), "p": pval, "sig": pval < 0.05})

    print("population\tn_responders\tn_non_responders\tp_value\tsignificant")
    for s in stats:
        pstr = "%.4f" % s["p"] if s["p"] is not None else "-"
        print(f"{s['pop']}\t{s['n_yes']}\t{s['n_no']}\t{pstr}\t{'yes' if s['sig'] else 'no'}")

    fig, axes = plt.subplots(2, 3, figsize=(10, 6))
    for i, p in enumerate(POPS):
        ax = axes.flatten()[i]
        ax.boxplot([by_pop[p]["yes"], by_pop[p]["no"]], labels=["Responders", "Non-responders"])
        ax.set_ylabel("%")
        ax.set_title(p)
    axes.flatten()[5].axis("off")
    plt.tight_layout()
    plt.savefig(BASE_DIR / "responder_comparison.png", dpi=120)
    plt.close()
