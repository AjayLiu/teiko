import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "cell_counts.db"
POPS = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]

if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte FROM samples ORDER BY id")
    print("sample\ttotal_count\tpopulation\tcount\tpercentage")
    for row in cur:
        counts = [row[i] for i in range(1, 6)]
        total = sum(counts)
        if total == 0:
            continue
        for pop, c in zip(POPS, counts):
            print(f"{row[0]}\t{total}\t{pop}\t{c}\t{(c/total)*100:.4f}")
    conn.close()
