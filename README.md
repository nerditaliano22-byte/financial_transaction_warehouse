# Financial Transaction Data Warehouse 📊

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Docker](https://img.shields.io/badge/Docker-Enabled-blueviolet)
![Status](https://img.shields.io/badge/Status-Prototype-green)

## 📌 Overview
This project is an end-to-end **Data Engineering** solution designed to transform raw financial transaction logs into a structured **Data Warehouse** for analytical querying.

The system implements a **Star Schema** architecture to optimize performance for OLAP workloads and serves insights via an interactive **Streamlit** dashboard. It demonstrates a complete data lifecycle: from raw CSV extraction to multidimensional modeling and visualization.

## 🏗️ Architecture

The pipeline follows a strict **ETL (Extract, Transform, Load)** workflow:

1.  **Extract**: Ingest raw account statements and auxiliary tables (Symbols, Countries) from the `data/` layer.
2.  **Transform**:
    * **Data Cleaning**: Standardization of country names and removal of artifacts.
    * **Modeling**: Creation of Dimension Tables (`dim_time`, `dim_symbol`, `dim_geography`) and a central Fact Table (`fact_transactions`).
    * **Enrichment**: Derivation of fiscal quarters and surrogate keys to ensure referential integrity.
3.  **Load**: Persist the processed Star Schema back to CSV (ready for DB ingestion) and load into the Dashboard.

### 🌟 Data Model (Star Schema)
* **Fact Table**: `fact_transactions` (Measures: *Units*, *TransactionCount*)
* **Dimensions**:
    * `dim_time`: Hierarchical time tracking (Date → Quarter).
    * `dim_symbol`: Security details (Sector, Industry).
    * `dim_geography`: Regional aggregation (Country → Region).

## 🚀 Getting Started

You can run this project locally or via Docker (Recommended for reproducibility).

### Option A: 🐳 Run with Docker (Recommended)
Ensure **Docker** and **Docker Compose** are installed.

1.  **Build and Run the Container:**
    ```bash
    docker-compose up --build
    ```
2.  **Access the Dashboard:**
    Open your browser at `http://localhost:8501`.

### Option B: 🐍 Run Locally
**Prerequisites:** Python 3.10+

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/financial-transaction-warehouse.git](https://github.com/YOUR_USERNAME/financial-transaction-warehouse.git)
    cd financial-transaction-warehouse
    ```

2.  **Create Virtual Environment:**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the ETL Pipeline:**
    *Generates the Star Schema files in the `data/` folder.*
    ```bash
    python src/etl.py
    ```

5.  **Launch the Dashboard:**
    ```bash
    streamlit run app.py
    ```

## 📂 Project Structure

```text
financial-transaction-warehouse/
├── data/                  # Raw inputs & Star Schema outputs (CSV)
├── notebooks/             # Jupyter Notebooks for EDA & Prototyping
├── src/
│   └── etl.py             # Core ETL logic (Pandas)
├── app.py                 # Streamlit Dashboard Entry Point
├── Dockerfile             # Container definition
├── docker-compose.yml     # Service orchestration
├── requirements.txt       # Python dependencies
└── README.md              # Project Documentation
