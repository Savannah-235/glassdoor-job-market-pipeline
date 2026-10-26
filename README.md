# Glassdoor Job Market Sanitisation Pipeline

An automated data engineering extraction and data transformation pipeline built in Python utilizing absolute operating system file orchestration and relational SQLite database query frameworks. The engine takes an uncleaned, text-heavy dataset tracking job postings and systematically refactors embedded layout structures, structural anomalies, and concatenated text breaks into clear metrics ready for visualisations and further analysis.

## Key Engineering Accomplishments
* Absolute File Pathing: Utilizes Python's native os.path utilities to construct immutable absolute paths, preventing file pathing system reference execution failures across divergent folder directory layers.
* Multi-Tier Relational Processing: Deploys isolated relational data environments by separating raw text streams inside a staging table (staging_jobs) before committing sanitised operations into a production layer table (clean_jobs).
* Advanced SQL String Parsing: Employs deep nested query execution structures using SUBSTR, INSTR, and REPLACE equations to cut away string indicators and isolate raw integer intervals from complex salary range blocks.
* Layout Break Elimination: Intercepts hidden data newline indicators via CHAR(10) computer character flags to separate squished brand characters from their underlying rating metadata scores cleanly.

## System Architecture & Logic Breakdown

### 1. File Isolation & Relational Table Staging
The extraction phase identifies system paths automatically and drops target record fields into an uncleaned SQL database staging table layout to preserve raw integrity:
```python
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, 'Uncleaned_DS_jobs.csv')

# Loaded cleanly into the local staging database structure
cursor.execute("CREATE TABLE staging_jobs (...);")
```

### 2. Algorithmic Data Range Isolation
Salary column intervals matching string structures like "115K-145K" are parsed by calculating position indexes via INSTR, slicing characters via SUBSTR, and replacing string variables before type-casting values:
```sql
CAST(REPLACE(REPLACE(SUBSTR(salary_estimate, 1, INSTR(salary_estimate, '-') - 1), 'K', ''), '\$', '') AS INTEGER) AS min_salary_thousands
```

### 3. Whitespace & Newline Character Interception
Embedded newline anomalies splitting business descriptions from rating elements are isolated by locating the character ten index array position and cutting the data bounds right before the text break:
```sql
CASE 
    WHEN INSTR(company_name, CHAR(10)) > 0 
    THEN TRIM(SUBSTR(company_name, 1, INSTR(company_name, CHAR(10)) - 1))
    ELSE TRIM(company_name)
END AS company_clean_name
```

## Setup & Execution Instructions

### Pipeline Processing Execution
Run the complete automated script directly from your terminal session inside the folder workspace:
```bash
python3 pipeline.py
```

### Terminal Data Verification
Inspect the compiled results inside your production tables using your command line database tools:
```bash
sqlite3 job_market_intelligence.db
```
Inside the sqlite terminal prompt, configure your visual spacing columns and run a verification lookup:
```sql
.mode column
.headers on
SELECT company_clean_name, min_salary_thousands, max_salary_thousands, company_rating FROM clean_jobs LIMIT 3;
```

## Business Dashboard Readiness
The final output engine changes missing data characters or broken fields like "-1" into clean default database tracking properties (like integer 0 values or "Unknown" string labels). This workflow structure completely eliminates skewed calculations or failed chart views during analytics phases. 
