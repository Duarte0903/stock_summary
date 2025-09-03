import base64
import os
import dotenv

from fetch_data import fetch_data
from process_stock_data import analyze_stocks_with_gemini
from send_email import format_stock_analysis_email, send_email

def main(request): 
    print("Starting the script...")

    message = request.get_json(silent=True)
    if message and "data" in message:
        decoded_message = base64.b64decode(message["data"]).decode("utf-8")
        print(f"Received Pub/Sub message: {decoded_message}")

    stocks_data = fetch_data()
    print("Data fetched successfully.")

    dotenv.load_dotenv()
    api_key = os.getenv("GEMINI")
    print("API key loaded successfully.")
    email_password = os.getenv("EMAIL")
    print("Email password loaded successfully.")

    api_response = analyze_stocks_with_gemini(stocks_data, api_key)
    print("Analysis completed.")

    email_content = format_stock_analysis_email(api_response)
    send_email(
        recipient="duarte0903@gmail.com",
        subject=email_content["subject"],
        body=email_content["html"],
        password=email_password
    )