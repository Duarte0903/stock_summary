
# Stock Summary Service

This project collects stock data, processes it, and sends summaries by email automatically. Deployment is done on Google Cloud Run and scheduling via Cloud Scheduler.

## Features

- Fetches stock data using `yfinance`
- Processes the collected data
- Sends summary by email
- Automated deployment on Google Cloud Run
- Daily scheduling via Cloud Scheduler

## Structure

- `fetch_data.py`: Fetches stock data.
- `process_stock_data.py`: Processes the collected data.
- `send_email.py`: Sends the summary by email.
- `main.py`: Orchestrates the main workflow.
- `deploy_gcp.ps1`: PowerShell script for GCP deployment.

## How to run locally

1. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
2. Run the service:
   ```powershell
   python main.py
   ```

## Deploy to Google Cloud Run

1. Configure your GCP project and authentication.
2. Run the deployment script:
   ```powershell
   .\deploy_gcp.ps1
   ```

## Scheduling

The service is triggered daily at 09:00 UTC via Cloud Scheduler. Update the deployment script for a different schedule.
