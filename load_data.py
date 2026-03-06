import csv
import sqlite3
from pathlib import Path
from typing import Optional


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "cell-count.csv"
DB_PATH = BASE_DIR / "cell_counts.db"



def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON;")

    cur = conn.cursor()
    cur.executescript(
        """
        DROP TABLE IF EXISTS samples;
        DROP TABLE IF EXISTS subjects;
        DROP TABLE IF EXISTS projects;

        CREATE TABLE projects (
            id TEXT PRIMARY KEY
        );

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
        """
    )
    conn.commit()


def _to_int(value: str) -> Optional[int]:
    value = value.strip()
    if value == "":
        return None
    return int(value)


def _to_str_or_none(value: str) -> Optional[str]:
    value = value.strip()
    return value if value != "" else None

def load_csv_into_db(conn: sqlite3.Connection, csv_path: Path) -> None:
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV file not found at {csv_path}")

    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Insert projects
            cur.execute(
                "INSERT OR IGNORE INTO projects (id) VALUES (?);",
                (row["project"],),
            )

            # Insert subjects
            cur.execute(
                """
                INSERT OR IGNORE INTO subjects (
                    id, project_id, condition, age, sex, treatment, response
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    row["subject"],
                    row["project"],
                    row["condition"],
                    _to_int(row["age"]),
                    row["sex"],
                    _to_str_or_none(row["treatment"]),
                    _to_str_or_none(row["response"]),
                ),
            )

            # Insert samples
            cur.execute(
                """
                INSERT OR REPLACE INTO samples (
                    id,
                    subject_id,
                    sample_type,
                    time_from_treatment_start,
                    b_cell,
                    cd8_t_cell,
                    cd4_t_cell,
                    nk_cell,
                    monocyte
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    row["sample"],
                    row["subject"],
                    row["sample_type"],
                    _to_int(row["time_from_treatment_start"]),
                    _to_int(row["b_cell"]),
                    _to_int(row["cd8_t_cell"]),
                    _to_int(row["cd4_t_cell"]),
                    _to_int(row["nk_cell"]),
                    _to_int(row["monocyte"]),
                ),
            )

    conn.commit()


def main() -> None:
    if not CSV_PATH.is_file():
        raise FileNotFoundError(f"Expected CSV file at {CSV_PATH}")

    with sqlite3.connect(DB_PATH) as conn:
        init_db(conn)
        load_csv_into_db(conn, CSV_PATH)


if __name__ == "__main__":
    main()