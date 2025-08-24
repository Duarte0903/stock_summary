from datetime import datetime
from typing import Dict
import smtplib
from email.mime.text import MIMEText
import markdown

def format_stock_analysis_email(gemini_response: Dict, recipient_name: str = "Investor") -> Dict[str, str]:
    """
    Convert Gemini stock analysis response into a nicely formatted HTML email with tables.
    """
    if not gemini_response.get('success', False):
        subject = "Stock Analysis - Error Report"
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.5;">
            <p>Dear {recipient_name},</p>
            <p>I attempted to generate your stock analysis report, but encountered an error:</p>
            <p><b>Error:</b> {gemini_response.get('error', 'Unknown error')}<br>
               <b>Details:</b> {gemini_response.get('message', 'No additional details')}</p>
            <p>Please check your API configuration and try again.</p>
            <p>Best regards,<br>Stock Analysis System</p>
        </body>
        </html>
        """
        return {"subject": subject, "html": html}

    stock_summary_lines = gemini_response.get('stock_summary', '').splitlines()
    stock_summary_list = []
    for line in stock_summary_lines:
        if "MARKET CONTEXT" in line:
            break
        if ":" in line:
            stock_summary_list.append(line)
    stock_rows = ""
    for line in stock_summary_list:
        stock, info = line.split(":", 1)
        price_vol = info.strip().split("|")
        price = price_vol[0].replace("Price", "").strip()
        volume = price_vol[1].replace("Volume", "").strip() if len(price_vol) > 1 else "-"
        stock_rows += f"""
            <tr style="text-align: center;">
                <td style="padding: 8px; border: 1px solid #ddd;">{stock}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{price}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{volume}</td>
            </tr>
        """

    market_context_list = [line for line in gemini_response.get('stock_summary', '').splitlines() if "MARKET CONTEXT" in line or "Average" in line or "Price Range" in line]
    market_rows = ""
    for line in market_context_list[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            market_rows += f"""
                <tr style="text-align: center;">
                    <td style="padding: 8px; border: 1px solid #ddd;">{key.strip()}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{value.strip()}</td>
                </tr>
            """

    ai_analysis_html = markdown.markdown(gemini_response.get('ai_analysis', ''))

    subject = "📊 Stock Portfolio Analysis Report"
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.5; color: #333;">
        <h2 style="color: #2E86C1;">Hello {recipient_name},</h2>
        <p>I've completed the AI-powered analysis of your stock portfolio as of {timestamp}. Here are the details:</p>

        <h3 style="color: #2E86C1;">Current Stock Data</h3>
        <table style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #2E86C1; color: white; text-align: center;">
                <th style="padding: 8px; border: 1px solid #ddd;">Stock</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Price (USD)</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Volume</th>
            </tr>
            {stock_rows}
        </table>

        <h3 style="color: #2E86C1;">Market Context</h3>
        <table style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #2E86C1; color: white; text-align: center;">
                <th style="padding: 8px; border: 1px solid #ddd;">Metric</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Value</th>
            </tr>
            {market_rows}
        </table>

        <h3 style="color: #2E86C1;">Key AI Findings</h3>
        <div style="background-color: #F2F3F4; padding: 10px; border-radius: 5px;">
            {ai_analysis_html}
        </div>

        <h3 style="color: #E74C3C;">Disclaimers</h3>
        <ul>
            <li>This analysis is for educational purposes only and should not be considered financial advice.</li>
            <li>Consult a qualified financial advisor before making any investment decisions.</li>
        </ul>

        <p>Token usage for this report: {gemini_response.get('api_response', {}).get('usageMetadata', {}).get('totalTokenCount', '-')}</p>
        <p>Best regards,<br>Stock Analysis System</p>
    </body>
    </html>
    """

    return {"subject": subject, "html": html}

def send_email(recipient: str, subject: str, body: str, password):
    """Send an email with the given subject and body to the recipient."""
    try:
        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["From"] = "duarte0903@gmail.com"
        msg["To"] = recipient

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("duarte0903@gmail.com", password)
            server.send_message(msg)

        print(f"Email sent successfully to {recipient}!")
    except Exception as e:
        print(f"Failed to send email: {e}")
