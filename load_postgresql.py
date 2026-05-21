import os
from pathlib import Path

import pandas as pd

from CRUD_Python_Module import PostgresAnimalShelter, psycopg


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "dogs_dataset.csv"
SCHEMA_FILE = BASE_DIR / "schema.sql"


def main():
    dsn = os.getenv("POSTGRES_DSN")
    if not dsn:
        raise RuntimeError("Set the POSTGRES_DSN environment variable before running this loader.")
    if psycopg is None:
        raise RuntimeError("psycopg is not installed. Install it with 'pip install psycopg[binary]'.")

    shelter = PostgresAnimalShelter(dsn)
    dataframe = pd.read_csv(DATA_FILE)

    with shelter._get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(SCHEMA_FILE.read_text(encoding="utf-8"))
            cursor.execute(f"TRUNCATE TABLE {shelter.table_name}")

            rows = list(dataframe.itertuples(index=False, name=None))
            cursor.executemany(
                f"""
                INSERT INTO {shelter.table_name} (
                    animal_id,
                    name,
                    animal_type,
                    breed,
                    age_upon_outcome_in_weeks,
                    color,
                    sex_upon_outcome,
                    outcome_type,
                    intake_type,
                    intake_condition,
                    location_lat,
                    location_long
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                rows,
            )
        connection.commit()

    print(f"Loaded {len(dataframe)} rows into PostgreSQL table '{shelter.table_name}'.")


if __name__ == "__main__":
    main()
