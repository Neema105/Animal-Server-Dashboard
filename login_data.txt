import os
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # error check
    psycopg = None
    dict_row = None


FILTER_DEFINITIONS = {
    "RESET": {
        "animal_type": "Dog",
        "breeds": [],
        "max_age_weeks": None,
    },
    "WATER": {
        "animal_type": "Dog",
        "breeds": ["Labrador Retriever Mix", "Chesapeake Bay Retriever", "Newfoundland"],
        "max_age_weeks": 104,
    },
    "MOUNTAIN": {
        "animal_type": "Dog",
        "breeds": ["German Shepherd", "Alaskan Malamute", "Siberian Husky"],
        "max_age_weeks": 104,
    },
    "DISASTER": {
        "animal_type": "Dog",
        "breeds": ["Doberman Pinscher", "Belgian Malinois", "Bloodhound"],
        "max_age_weeks": 104,
    },
}


class BaseAnimalShelter:
    def get_dashboard_data(self, filter_type: str = "RESET") -> pd.DataFrame:
        raise NotImplementedError

    def create(self, data: Dict[str, Any]) -> bool:
        raise NotImplementedError

    def read(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def update(self, query: Dict[str, Any], new_values: Dict[str, Any]) -> int:
        raise NotImplementedError

    def delete(self, query: Dict[str, Any]) -> int:
        raise NotImplementedError


class CSVAnimalShelter(BaseAnimalShelter):
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self._df = pd.read_csv(csv_path)

    def get_dashboard_data(self, filter_type: str = "RESET") -> pd.DataFrame:
        filter_config = FILTER_DEFINITIONS.get(filter_type, FILTER_DEFINITIONS["RESET"])
        filtered = self._df[self._df["animal_type"] == filter_config["animal_type"]]

        if filter_config["breeds"]:
            filtered = filtered[filtered["breed"].isin(filter_config["breeds"])]

        if filter_config["max_age_weeks"] is not None:
            filtered = filtered[filtered["age_upon_outcome_in_weeks"] <= filter_config["max_age_weeks"]]

        return filtered.copy()

    def create(self, data: Dict[str, Any]) -> bool:
        if not data:
            return False
        self._df = pd.concat([self._df, pd.DataFrame([data])], ignore_index=True)
        return True

    def read(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        data = self._df
        for column, value in (query or {}).items():
            data = data[data[column] == value]
        return data.to_dict("records")

    def update(self, query: Dict[str, Any], new_values: Dict[str, Any]) -> int:
        if not query or not new_values:
            return 0

        mask = pd.Series(True, index=self._df.index)
        for column, value in query.items():
            mask &= self._df[column] == value

        updated_rows = int(mask.sum())
        for column, value in new_values.items():
            self._df.loc[mask, column] = value
        return updated_rows

    def delete(self, query: Dict[str, Any]) -> int:
        if not query:
            return 0

        mask = pd.Series(True, index=self._df.index)
        for column, value in query.items():
            mask &= self._df[column] == value

        deleted_rows = int(mask.sum())
        self._df = self._df.loc[~mask].reset_index(drop=True)
        return deleted_rows


class PostgresAnimalShelter(BaseAnimalShelter):
    table_name = "animals"

    def __init__(self, dsn: str):
        if psycopg is None:
            raise RuntimeError("psycopg is not installed. Install it with 'pip install psycopg[binary]'.")
        self.dsn = dsn

    def _get_connection(self):
        return psycopg.connect(self.dsn, row_factory=dict_row)

    def _build_where_clause(self, query: Optional[Dict[str, Any]] = None):
        query = query or {}
        clauses = []
        params: List[Any] = []

        for column, value in query.items():
            if isinstance(value, Iterable) and not isinstance(value, (str, bytes, dict)):
                value_list = list(value)
                if not value_list:
                    continue
                clauses.append(f"{column} = ANY(%s)")
                params.append(value_list)
            else:
                clauses.append(f"{column} = %s")
                params.append(value)

        where_sql = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        return where_sql, params

    def get_dashboard_data(self, filter_type: str = "RESET") -> pd.DataFrame:
        filter_config = FILTER_DEFINITIONS.get(filter_type, FILTER_DEFINITIONS["RESET"])
        clauses = ["animal_type = %s"]
        params: List[Any] = [filter_config["animal_type"]]

        if filter_config["breeds"]:
            clauses.append("breed = ANY(%s)")
            params.append(filter_config["breeds"])

        if filter_config["max_age_weeks"] is not None:
            clauses.append("age_upon_outcome_in_weeks <= %s")
            params.append(filter_config["max_age_weeks"])

        query = f"""
            SELECT
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
            FROM {self.table_name}
            WHERE {' AND '.join(clauses)}
            ORDER BY animal_id
        """

        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                return pd.DataFrame(cursor.fetchall())

    def create(self, data: Dict[str, Any]) -> bool:
        if not data:
            return False

        columns = list(data.keys())
        values = [data[column] for column in columns]
        placeholders = ", ".join(["%s"] * len(columns))
        sql = f"""
            INSERT INTO {self.table_name} ({", ".join(columns)})
            VALUES ({placeholders})
        """

        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, values)
            connection.commit()
        return True

    def read(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        where_sql, params = self._build_where_clause(query)
        sql = f"SELECT * FROM {self.table_name}{where_sql} ORDER BY animal_id"

        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()

    def update(self, query: Dict[str, Any], new_values: Dict[str, Any]) -> int:
        if not query or not new_values:
            return 0

        assignments = ", ".join([f"{column} = %s" for column in new_values])
        update_params = list(new_values.values())
        where_sql, where_params = self._build_where_clause(query)
        sql = f"UPDATE {self.table_name} SET {assignments}{where_sql}"

        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, update_params + where_params)
                updated_rows = cursor.rowcount
            connection.commit()
        return updated_rows

    def delete(self, query: Dict[str, Any]) -> int:
        if not query:
            return 0

        where_sql, params = self._build_where_clause(query)
        sql = f"DELETE FROM {self.table_name}{where_sql}"

        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                deleted_rows = cursor.rowcount
            connection.commit()
        return deleted_rows


def build_animal_shelter(data_file: str) -> BaseAnimalShelter:
    postgres_dsn = os.getenv("POSTGRES_DSN")
    if postgres_dsn:
        try:
            return PostgresAnimalShelter(postgres_dsn)
        except Exception:
            pass
    return CSVAnimalShelter(data_file)
