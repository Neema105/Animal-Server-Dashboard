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


```powershell
python load_postgresql.py
```

```powershell
python app.py
```

