import csv
import os
import sqlite3

def run_pipeline():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'Uncleaned_DS_jobs.csv')
    db_path = os.path.join(base_dir, 'job_market_intelligence.db')

    if not os.path.exists(csv_path):
        print(f"Error: Missing source file at absolute path location: {csv_path}")
        return

    print("Initializing pipeline engine and establishing database connections...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS staging_jobs;")
    cursor.execute("DROP TABLE IF EXISTS clean_jobs;")

    cursor.execute("""
    CREATE TABLE staging_jobs (
        index_id TEXT,
        job_title TEXT,
        salary_estimate TEXT,
        job_description TEXT,
        rating TEXT,
        company_name TEXT,
        location TEXT,
        headquarters TEXT,
        size TEXT,
        founded TEXT,
        type_of_ownership TEXT,
        industry TEXT,
        sector TEXT,
        revenue TEXT,
        competitors TEXT
    );
    """)

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        insert_query = "INSERT INTO staging_jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        for row in reader:
            if len(row) == 15:
                cursor.execute(insert_query, row)
    
    conn.commit()
    print("Raw staging load complete. Streaming source metrics populated to staging_jobs.")

    print("Executing structural SQL string transformations and type-casting matrices...")
    
    transform_query = """
    CREATE TABLE clean_jobs AS
    SELECT 
        CAST(index_id AS INTEGER) AS job_id,
        TRIM(job_title) AS job_title,
        
        CASE 
            WHEN salary_estimate = '-1' OR salary_estimate LIKE '%Unknown%' THEN 0
            ELSE CAST(REPLACE(REPLACE(SUBSTR(salary_estimate, 1, INSTR(salary_estimate, '-') - 1), 'K', ''), '$', '') AS INTEGER)
        END AS min_salary_thousands,
        
        CASE 
            WHEN salary_estimate = '-1' OR salary_estimate LIKE '%Unknown%' THEN 0
            ELSE CAST(REPLACE(REPLACE(SUBSTR(
                salary_estimate, 
                INSTR(salary_estimate, '-') + 1, 
                INSTR(salary_estimate, ' (') - INSTR(salary_estimate, '-') - 1
            ), 'K', ''), '$', '') AS INTEGER)
        END AS max_salary_thousands,

        CASE 
            WHEN INSTR(company_name, CHAR(10)) > 0 
            THEN TRIM(SUBSTR(company_name, 1, INSTR(company_name, CHAR(10)) - 1))
            ELSE TRIM(company_name)
        END AS company_clean_name,

        CASE 
            WHEN rating = '-1' THEN 0.0
            ELSE CAST(rating AS REAL)
        END AS company_rating,

        TRIM(location) AS job_location,
        
        CASE WHEN headquarters = '-1' THEN 'Unknown' ELSE TRIM(headquarters) END AS company_headquarters,
        CASE WHEN size = '-1' OR size = 'Unknown/Non-Applicable' THEN 'Unknown' ELSE TRIM(size) END AS company_size,
        CASE WHEN founded = '-1' THEN 0 ELSE CAST(founded AS INTEGER) END AS year_founded,
        CASE WHEN type_of_ownership = '-1' THEN 'Unknown' ELSE TRIM(type_of_ownership) END AS ownership_type,
        CASE WHEN industry = '-1' THEN 'Unknown' ELSE TRIM(industry) END AS industry_classification,
        CASE WHEN sector = '-1' THEN 'Unknown' ELSE TRIM(sector) END AS economy_sector,
        CASE WHEN revenue = '-1' OR revenue = 'Unknown / Non-Applicable' THEN 'Unknown' ELSE TRIM(revenue) END AS annual_revenue,
        job_description

    FROM staging_jobs;
    """

    cursor.execute(transform_query)
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM clean_jobs;")
    total_records = cursor.fetchone()[0]
    
    conn.close()
    print(f"Pipeline processing complete! {total_records} records sanitized and compiled inside clean_jobs table.")

if __name__ == '__main__':
    run_pipeline()
