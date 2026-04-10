# Compliance at a Glance

A Snowflake-powered Streamlit dashboard that provides compliance officers with instant visibility into contract expirations, risk levels, and financial exposure. This project was developed for the CSEGSA Hackathon 2026.

## Live Application

- **Streamlit Dashboard:** [Open Compliance at a Glance](https://app.snowflake.com/streamlit/kgtinyl/eb87883/#/apps/pbxsrc6e55e3v5pm4c5e)

## Problem Statement

Legal teams often manage hundreds of contracts without a centralized view of what is expiring, high-risk, or financially significant. This dashboard helps compliance officers monitor contract portfolios and make informed decisions.


## Objectives

This solution addresses the following requirements:

- Identify contracts expiring in the next 30, 60, and 90 days
- Filter contracts by risk level (High, Medium, Low)
- Display total contract value at risk by category
- Provide an interactive Streamlit dashboard
- Highlight auto-renewing contracts requiring review (Bonus)

## Tech Stack

- **Snowflake** – Data storage and analytics platform
- **Snowflake SQL** – Data transformation and analysis
- **Snowpark Python** – Data access and processing
- **Streamlit in Snowflake** – Interactive dashboard development
- **Pandas** – Data manipulation
- **GitHub** – Version control and project submission

## Dataset

**File:** `contract_metadata.csv`  
**Records:** 150 contracts

**Columns:**
- contract_id
- vendor_name
- category
- contract_value_usd
- start_date
- end_date
- governing_law
- liability_cap_usd
- auto_renews
- risk_flags
- risk_level
- owner_team


## Key Features

- **Expiry Risk Overview** – Contracts categorized into Expired, 0–30, 31–60, 61–90, and 90+ day buckets.
- **Risk Level Filtering** – Interactive filtering by High, Medium, and Low risk levels.
- **Financial Exposure Analysis** – Total contract value summarized by category.
- **Critical Contract Identification** – Custom risk scoring highlights high-priority contracts.
- **Auto-Renew Alerts** – Flags contracts set to auto-renew within 60 days.
- **Executive Summary** – Provides actionable insights for decision-makers.


## Architecture

```text
contract_metadata.csv
    ↓
Snowflake Table
    ↓
SQL Analysis
    ↓
Streamlit Dashboard
```


## Setup Instructions

### 1. Create Database and Schema
```sql
CREATE DATABASE IF NOT EXISTS HACKATHON;
CREATE SCHEMA IF NOT EXISTS HACKATHON.DATA;

CREATE OR REPLACE TABLE HACKATHON.DATA.CONTRACT_METADATA (
    CONTRACT_ID STRING,
    VENDOR_NAME STRING,
    CATEGORY STRING,
    CONTRACT_VALUE_USD FLOAT,
    START_DATE DATE,
    END_DATE DATE,
    GOVERNING_LAW STRING,
    LIABILITY_CAP_USD FLOAT,
    AUTO_RENEWS BOOLEAN,
    RISK_FLAGS STRING,
    RISK_LEVEL STRING,
    OWNER_TEAM STRING
);

```

## Deployment Instructions

### **3. Load the Dataset**

Upload `contract_metadata.csv` using the Snowflake UI.

**Steps:**

1. Navigate to **Data → Add Data → Load Data into a Table**.
2. Upload the file `contract_metadata.csv`.
3. Configure the table with the following settings:

| Parameter    | Value               |
| ------------ | ------------------- |
| **Database** | `HACKATHON`         |
| **Schema**   | `DATA`              |
| **Table**    | `CONTRACT_METADATA` |

4. Review the detected schema and click **Load** to import the dataset.

### **4. Deploy the Streamlit App**

Create and run the Streamlit dashboard directly within Snowflake.

**Steps:**

1. Navigate to **Projects → Streamlit in Snowflake**.
2. Click **Create Streamlit App**.
3. Configure the application with the following settings:

| Parameter     | Value        |
| ------------- | ------------ |
| **Database**  | `HACKATHON`  |
| **Schema**    | `DATA`       |
| **Warehouse** | `COMPUTE_WH` |

4. Open the default `streamlit_app.py` file.
5. Copy and paste the contents of your `streamlit_app.py` script into the editor.
6. Click **Run** to launch the dashboard.

### Verification

Once deployed, confirm that the dashboard displays:

* Contracts expiring in 30, 60, and 90 days
* Filters by risk level, category, and owner team
* Financial exposure by contract category
* Auto-renew contracts requiring review
* An interactive compliance dashboard powered by Snowflake


