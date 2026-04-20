# PostgreSQL Setup

## 1. Install the PostgreSQL driver

```powershell
pip install psycopg[binary]
```

## 2. Create a PostgreSQL database

Example:

```sql
CREATE DATABASE cs499_dashboard;
```

## 3. Set the connection string

PowerShell example:

```powershell
$env:POSTGRES_DSN = "dbname=cs499_dashboard user=postgres password=your_password host=localhost port=5432"
```

## 4. Load the dataset into PostgreSQL

```powershell
python load_postgresql.py
```

This will:
- create the `animals` table from [schema.sql](/C:/Users/neema/PycharmProjects/CS499/schema.sql)
- add indexes for the dashboard filters
- import all rows from `dogs_dataset.csv`

## 5. Run the dashboard

```powershell
python app.py
```

When `POSTGRES_DSN` is set, the dashboard reads animal data from PostgreSQL. If it is not set, the app falls back to the CSV so development can continue without a database.

## Why this improves the project

- It separates storage from presentation, which is a stronger architecture than reading a flat file directly in the UI.
- Dashboard filters now map cleanly to SQL queries, which is closer to how production dashboards work.
- PostgreSQL can scale better than CSV for filtering, indexing, and future joins.
- The CRUD layer is now reusable for additional reports, inserts, updates, and deletes.
- The indexed schema makes repeated filter operations more efficient as the dataset grows.
