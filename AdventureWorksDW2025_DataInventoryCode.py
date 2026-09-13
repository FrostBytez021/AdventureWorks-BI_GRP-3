import pyodbc
import pandas as pd

# 1. Connect (tries Driver 18 first, falls back to 17)
def get_connection():
    drivers_to_try = ["ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server"]
    last_error = None
    for driver in drivers_to_try:
        conn_str = (
            f"DRIVER={{{driver}}};"
            "SERVER=localhost;"
            "DATABASE=AdventureWorksDW2025;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
        try:
            return pyodbc.connect(conn_str)
        except pyodbc.Error as e:
            last_error = e
            continue
    raise RuntimeError(f"Could not connect with any known driver. Last error: {last_error}")

conn = get_connection()
cursor = conn.cursor()

# 2. Discover ALL user tables (excludes views and system tables)
tables_df = pd.read_sql("""
    SELECT TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
    ORDER BY TABLE_NAME;
""", conn)
all_tables = tables_df['TABLE_NAME'].tolist()
print(f"Found {len(all_tables)} tables: {all_tables}\n")

# 3. Profile each table
results = []

for table in all_tables:
    print(f"Profiling {table}...")

    # --- Row count ---
    row_count = pd.read_sql(f"SELECT COUNT(*) AS cnt FROM [{table}]", conn)['cnt'][0]

    # --- Data types (as a readable summary string) ---
    dtypes_df = pd.read_sql(f"""
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = '{table}'
        ORDER BY ORDINAL_POSITION;
    """, conn)
    data_types_summary = ", ".join(dtypes_df['DATA_TYPE'].unique())
    all_columns = dtypes_df['COLUMN_NAME'].tolist()

    # --- Primary key ---
    pk_df = pd.read_sql(f"""
        SELECT kcu.COLUMN_NAME
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
            ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
        WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY' AND tc.TABLE_NAME = '{table}'
        ORDER BY kcu.ORDINAL_POSITION;
    """, conn)
    pk_columns = pk_df['COLUMN_NAME'].tolist()
    pk_summary = " + ".join(pk_columns) if pk_columns else "None declared"

    # --- Duplicates (based on PK if it exists, else full-row check) ---
    if pk_columns:
        key_cols = ", ".join(f"[{c}]" for c in pk_columns)
        dup_df = pd.read_sql(f"""
            SELECT COUNT(*) AS dup_groups FROM (
                SELECT {key_cols} FROM [{table}]
                GROUP BY {key_cols} HAVING COUNT(*) > 1
            ) x;
        """, conn)
        duplicates = f"{dup_df['dup_groups'][0]} duplicate key groups"
    else:
        all_cols_str = ", ".join(f"[{c}]" for c in all_columns)
        dup_df = pd.read_sql(f"""
            SELECT COUNT(*) AS dup_rows FROM (
                SELECT {all_cols_str} FROM [{table}]
                GROUP BY {all_cols_str} HAVING COUNT(*) > 1
            ) x;
        """, conn)
        duplicates = f"{dup_df['dup_rows'][0]} duplicate full-row groups (no PK declared)"

    # --- Outliers (numeric columns only, IQR method) ---
    numeric_cols = dtypes_df[dtypes_df['DATA_TYPE'].isin(
        ['int', 'bigint', 'smallint', 'tinyint', 'float', 'money', 'decimal', 'numeric', 'real']
    )]['COLUMN_NAME'].tolist()

    outlier_notes = []
    if numeric_cols and row_count > 0:
        cols_str = ", ".join(f"[{c}]" for c in numeric_cols)
        try:
            numeric_data = pd.read_sql(f"SELECT {cols_str} FROM [{table}]", conn)
            for col in numeric_cols:
                series = numeric_data[col].dropna()
                if len(series) < 4:
                    continue
                q1, q3 = series.quantile(0.25), series.quantile(0.75)
                iqr = q3 - q1
                if iqr == 0:
                    continue
                lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                outlier_count = ((series < lower) | (series > upper)).sum()
                if outlier_count > 0:
                    pct = round(outlier_count / len(series) * 100, 2)
                    outlier_notes.append(f"{col}: {outlier_count} ({pct}%)")
        except Exception as e:
            outlier_notes.append(f"Could not evaluate ({e})")
    outliers_summary = "; ".join(outlier_notes) if outlier_notes else "None flagged"

    # --- Referential gaps (check every FK defined on this table) ---
    fk_df = pd.read_sql(f"""
        SELECT
            fk_col.name AS fk_column,
            pk_tab.name AS referenced_table,
            pk_col.name AS referenced_column
        FROM sys.foreign_keys fk
        JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
        JOIN sys.tables fk_tab ON fkc.parent_object_id = fk_tab.object_id
        JOIN sys.columns fk_col ON fkc.parent_object_id = fk_col.object_id AND fkc.parent_column_id = fk_col.column_id
        JOIN sys.tables pk_tab ON fkc.referenced_object_id = pk_tab.object_id
        JOIN sys.columns pk_col ON fkc.referenced_object_id = pk_col.object_id AND fkc.referenced_column_id = pk_col.column_id
        WHERE fk_tab.name = '{table}';
    """, conn)

    gap_notes = []
    for _, fk_row in fk_df.iterrows():
        fk_col, ref_table, ref_col = fk_row['fk_column'], fk_row['referenced_table'], fk_row['referenced_column']
        gap_check = pd.read_sql(f"""
            SELECT COUNT(*) AS gaps
            FROM [{table}] f
            LEFT JOIN [{ref_table}] d ON f.[{fk_col}] = d.[{ref_col}]
            WHERE f.[{fk_col}] IS NOT NULL AND d.[{ref_col}] IS NULL;
        """, conn)
        gaps = gap_check['gaps'][0]
        if gaps > 0:
            gap_notes.append(f"{fk_col} -> {ref_table}: {gaps} orphaned")
    referential_gaps = "; ".join(gap_notes) if gap_notes else ("None (no FKs declared)" if fk_df.empty else "None found")

    results.append({
        "Table Name": table,
        "Source Row Count": row_count,
        "Data Types": data_types_summary,
        "Primary Key": pk_summary,
        "Duplicates": duplicates,
        "Outliers": outliers_summary,
        "Referential Gaps": referential_gaps
    })

conn.close()

# 4. Build final DataFrame, preview, export
inventory_df = pd.DataFrame(results)
print("\n" + "=" * 60)
print(inventory_df)

inventory_df.to_excel("AdventureWorksDW2025_DataInventory.xlsx", index=False, sheet_name="Data Inventory")