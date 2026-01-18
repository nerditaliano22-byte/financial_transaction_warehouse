import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Define paths for cleaner file management
DATA_DIR = "data"

def etl_pipeline():
    print("EXTRACT")
    # Load source CSVs from data directory
    symbols = pd.read_csv(os.path.join(DATA_DIR, "symbols.csv"), sep=';')
    account = pd.read_csv(os.path.join(DATA_DIR, "account-statement-1-1-2024-12-31-2024.csv"), sep=';')
    country = pd.read_csv(os.path.join(DATA_DIR, "country.csv"))

    # Standardize country names
    country['name'] = country['name'].replace({
        'Taiwan, Province of China': 'Taiwan',
        'Türkiye': 'Turkey'   
    })
    country.loc[(country['name'] == 'Taiwan') & (country['region'].isnull()), 'region'] = 'Asia'

    # Clean column names
    for df in (symbols, account, country):
        df.columns = df.columns.str.strip()

    # Drop "Unnamed" columns
    account = account.drop(columns=[c for c in account.columns if "Unnamed" in c], errors='ignore')

    print("TRANSFORM")
    # Filter to 2024 and BUY/SELL
    account['Date'] = pd.to_datetime(account['Date'], dayfirst=True, errors='coerce')
    acct_2024 = account[
        (account['Date'].dt.year == 2024) & (account['TransactionType'].isin(['BUY', 'SELL']))].copy()

    # Derived attributes
    acct_2024['Quarter'] = acct_2024['Date'].dt.quarter

    # Dim Time
    dim_time = (acct_2024[['Date', 'Quarter']]
                .drop_duplicates()
                .reset_index(drop=True))
    dim_time['TimeKey'] = dim_time.index + 1

    # Dim Symbol
    dim_symbol = (symbols[['symbol', 'sector', 'industry', 'country']]
                  .drop_duplicates()
                  .reset_index(drop=True))
    dim_symbol['SymbolKey'] = dim_symbol.index + 1
    dim_symbol = dim_symbol.rename(columns={'symbol':'Symbol','country':'Country'})

    # Dim Geography
    dim_geo = (country[['name','region']]
               .drop_duplicates()
               .reset_index(drop=True))
    dim_geo['GeographyKey'] = dim_geo.index + 1
    dim_geo = dim_geo.rename(columns={'name':'Country','region':'Region'})

    # Dim Transaction Type
    dim_trans = (acct_2024[['TransactionType']]
                 .drop_duplicates()
                 .reset_index(drop=True))
    dim_trans['TransactionTypeKey'] = dim_trans.index + 1

    # Build Fact Table
    fact = acct_2024.copy()
    fact = fact.merge(dim_time[['TimeKey', 'Date', 'Quarter']], on=['Date','Quarter'], how='left')
    fact = fact.merge(dim_symbol[['SymbolKey', 'Symbol']], left_on='Symbol', right_on='Symbol', how='left')
    fact = fact.merge(dim_symbol[['Symbol', 'Country']], on='Symbol', how='left')
    fact = fact.merge(dim_geo[['GeographyKey', 'Country']], on='Country', how='left')
    fact = fact.merge(dim_trans[['TransactionTypeKey', 'TransactionType']], on='TransactionType', how='left')

    # Finalize Fact Table
    fact_final = fact[['TimeKey','SymbolKey','GeographyKey','TransactionTypeKey','TransactionType','Unit']].copy()
    fact_final = fact_final.rename(columns={'Unit':'Units'})
    fact_final['FactTransactionKey'] = fact_final.index + 1
    fact_final['TransactionCount'] = 1  

    print("Fact table rows before dropna:", len(fact_final))
    fact_final = fact_final.dropna(subset=['TimeKey','SymbolKey','GeographyKey','TransactionTypeKey'])
    print("Fact table rows after dropna:", len(fact_final))

    print("ETL complete.")
    return {
        'fact': fact_final,
        'dim_time': dim_time,
        'dim_symbol': dim_symbol,
        'dim_geography': dim_geo,
        'dim_transaction_type': dim_trans
    }

def save_csv(dw):
    print("LOAD")
    # Save output to data directory
    dw['fact'].to_csv(os.path.join(DATA_DIR, "fact_transactions.csv"), index=False)
    dw['dim_time'].to_csv(os.path.join(DATA_DIR, "dim_time.csv"), index=False)
    dw['dim_symbol'].to_csv(os.path.join(DATA_DIR, "dim_symbol.csv"), index=False)
    dw['dim_geography'].to_csv(os.path.join(DATA_DIR, "dim_geography.csv"), index=False)
    dw['dim_transaction_type'].to_csv(os.path.join(DATA_DIR, "dim_transaction_type.csv"), index=False)
    print(f"CSV files saved successfully to {DATA_DIR}/")

def main():
    warehouse = etl_pipeline()
    # diagnostic(warehouse) # Uncomment if needed
    # plot_queries(warehouse) # Uncomment if needed
    save_csv(warehouse)

if __name__ == "__main__":
    main()