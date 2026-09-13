import pandas as pd
import pyodbc

# 1. CONFIGURATION
SERVER_NAME = "."  
DATABASE_NAME = "AdventureWorksDW2025"

# Target tables for the proj
TARGET_TABLES = [
    "DimCustomer",
    "DimDate",
    "DimEmployee",
    "DimGeography",
    "DimProduct_Combined",
    "DimPromotion",
    "DimReseller",
    "DimSalesReason",
    "DimSalesTerritory",
    "FactInternetSales",
    "FactInternetSalesReason",
    "FactResellerSales",
    "FactSalesQuota",
]

conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    f"Trusted_Connection=yes;"
)

# 2. METADATA EXTRACTOR FUNCTION
def get_data_dictionary():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    tables_formatted = "'" + "','".join(TARGET_TABLES) + "'"

    # Fetch schema metadata from SQL Server catalog
    metadata_query = f"""
    SELECT 
        t.name AS [TABLE NAME],
        c.name AS [ATTRIBUTE NAME],
        ISNULL(CAST(ep.value AS VARCHAR(255)), 'Column containing ' + c.name) AS [CONTENTS],
        UPPER(tp.name) AS [TYPE],
        CASE 
            WHEN tp.name IN ('date', 'datetime', 'datetime2') THEN 'YYYY-MM-DD'
            WHEN tp.name IN ('money', 'decimal', 'numeric', 'float') THEN 'Currency / Decimal'
            WHEN tp.name IN ('int', 'bigint', 'smallint', 'tinyint') THEN 'Integer'
            WHEN tp.name IN ('nvarchar', 'varchar', 'nchar', 'char') THEN 'Text'
            WHEN tp.name = 'bit' THEN 'Boolean (0/1)'
            ELSE tp.name
        END AS [FORMAT],
        CASE WHEN c.is_nullable = 0 THEN 'Yes' ELSE 'No' END AS [REQUIRED],
        ISNULL(
            (SELECT CASE WHEN k.type = 'PK' THEN 'PK' ELSE 'FK' END
             FROM sys.key_constraints k
             INNER JOIN sys.index_columns ic ON k.parent_object_id = ic.object_id AND k.unique_index_id = ic.index_id
             WHERE ic.object_id = c.object_id AND ic.column_id = c.column_id),
            ISNULL(
                (SELECT 'FK' 
                 FROM sys.foreign_key_columns fkc 
                 WHERE fkc.parent_object_id = c.object_id AND fkc.parent_column_id = c.column_id),
                'None'
            )
        ) AS [PK or FK],
        ISNULL(
            (SELECT OBJECT_NAME(fkc.referenced_object_id)
             FROM sys.foreign_key_columns fkc
             WHERE fkc.parent_object_id = c.object_id AND fkc.parent_column_id = c.column_id),
            'N/A'
        ) AS [FK REFERENCED TABLE]
    FROM sys.tables t
    INNER JOIN sys.columns c ON t.object_id = c.object_id
    INNER JOIN sys.types tp ON c.user_type_id = tp.user_type_id
    LEFT JOIN sys.extended_properties ep ON ep.major_id = c.object_id AND ep.minor_id = c.column_id AND ep.name = 'MS_Description'
    WHERE t.name IN ({tables_formatted})
    ORDER BY t.name, c.column_id;
    """

    df_meta = pd.read_sql(metadata_query, conn)
    ranges = []

    print("Extracting live RANGE (MIN to MAX) values directly from tables...")

    # Calculate exact MIN and MAX for every column
    for idx, row in df_meta.iterrows():
        tbl = row["TABLE NAME"]
        col = row["ATTRIBUTE NAME"]
        col_type = row["TYPE"]

        # Skip binary or complex blob datatypes if present
        if col_type in ["VARBINARY", "IMAGE", "VARBINARY(MAX)"]:
            ranges.append("N/A")
            continue

        range_query = f"SELECT MIN([{col}]), MAX([{col}]) FROM [{tbl}]"
        try:
            cursor.execute(range_query)
            min_val, max_val = cursor.fetchone()

            if min_val is None and max_val is None:
                ranges.append("All NULLs")
            elif min_val == max_val:
                ranges.append(f"{min_val}")
            else:
                ranges.append(f"{min_val} to {max_val}")
        except Exception:
            ranges.append("N/A")

    conn.close()

    # Insert calculated RANGE into the DataFrame
    df_meta["RANGE"] = ranges

    # Reorder columns to strictly match your required headers
    final_columns = [
        "TABLE NAME",
        "ATTRIBUTE NAME",
        "CONTENTS",
        "TYPE",
        "FORMAT",
        "RANGE",
        "REQUIRED",
        "PK or FK",
        "FK REFERENCED TABLE",
    ]
    df_meta = df_meta[final_columns]

    return df_meta

# 3. RUN & EXPORT
if __name__ == "__main__":
    df_dict = get_data_dictionary()

    # Save output to Markdown and CSV files
    csv_file = "AdventureWorksDW2025_DataDictionary.csv"

    df_dict.to_csv(csv_file, index=False)

    print(
        f"\nData Dictionary executed."
    )