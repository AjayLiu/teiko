import csv
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "cell-count.csv"
DB_PATH = BASE_DIR / "cell_counts.db"


def init_db(conn):
    cur = conn.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS samples;
        DROP TABLE IF EXISTS subjects;
        DROP TABLE IF EXISTS projects;

        CREATE TABLE projects (id TEXT PRIMARY KEY);

        CREATE TABLE subjects (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            condition TEXT NOT NULL,
            age INTEGER NOT NULL,
            sex TEXT NOT NULL,
            treatment TEXT,
            response TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        );

        CREATE TABLE samples (
            id TEXT PRIMARY KEY,
            subject_id TEXT NOT NULL,
            sample_type TEXT NOT NULL,
            time_from_treatment_start INTEGER NOT NULL,
            b_cell INTEGER NOT NULL,
            cd8_t_cell INTEGER NOT NULL,
            cd4_t_cell INTEGER NOT NULL,
            nk_cell INTEGER NOT NULL,
            monocyte INTEGER NOT NULL,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        );
    """)
    conn.commit()


def load_csv(conn, path):
    cur = conn.cursor()
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            cur.execute("INSERT OR IGNORE INTO projects (id) VALUES (?);", (row["project"],))
            cur.execute(
                "INSERT OR IGNORE INTO subjects (id, project_id, condition, age, sex, treatment, response) VALUES (?, ?, ?, ?, ?, ?, ?);",
                (row["subject"], row["project"], row["condition"], int(row["age"]), row["sex"], row["treatment"] or None, row["response"] or None),
            )
            cur.execute(
                "INSERT OR REPLACE INTO samples (id, subject_id, sample_type, time_from_treatment_start, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
                (row["sample"], row["subject"], row["sample_type"], int(row["time_from_treatment_start"]), int(row["b_cell"]), int(row["cd8_t_cell"]), int(row["cd4_t_cell"]), int(row["nk_cell"]), int(row["monocyte"])),
            )
    conn.commit()


if __name__ == "__main__":
    with sqlite3.connect(DB_PATH) as conn:
        init_db(conn)
        load_csv(conn, CSV_PATH)
