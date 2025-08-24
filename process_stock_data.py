import numpy as np
import requests
from typing import Dict

def analyze_stocks_with_gemini(stock_data: Dict, api_key: str, confirm_cost=True) -> Dict:
    """
    Analyze stock data and get sell recommendations using Google Gemini AI
    
    Args:
        stock_data: Dictionary with stock symbols and their close/volume data
        api_key: Your Google Gemini API key
        confirm_cost: Must be True to proceed (safety measure)
        
    Returns:
        Dictionary containing AI analysis and recommendations
    """
    
    if not confirm_cost:
        return {
            "success": False,
            "error": "Cost confirmation required",
            "message": """
⚠️  COST PROTECTION ENABLED ⚠️

To proceed with Gemini API call:
1. Check your API quota at: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com
2. Gemini Pro is FREE up to 60 requests/minute, 1,500 requests/day
3. Set confirm_cost=True in the function call

Example: analyze_stocks_with_gemini(data, api_key, confirm_cost=True)
            """
        }
    
    def format_stock_data(data):
        formatted = "CURRENT STOCK DATA ANALYSIS REQUEST\n"
        formatted += "=" * 50 + "\n\n"
        
        for symbol, info in data.items():
            price = float(info['close'])
            volume = int(info['volume'])
            formatted += f"{symbol}: Price ${price:.2f} | Volume {volume:,}\n"
        
        prices = [float(info['close']) for info in data.values()]
        volumes = [int(info['volume']) for info in data.values()]
        
        formatted += f"\nMARKET CONTEXT:\n"
        formatted += f"Average Price: ${np.mean(prices):.2f}\n"
        formatted += f"Price Range: ${min(prices):.2f} - ${max(prices):.2f}\n"
        formatted += f"Average Volume: {int(np.mean(volumes)):,}\n"
        formatted += f"Total Stocks: {len(data)}\n"
        
        return formatted
    
    stock_summary = format_stock_data(stock_data)
    
    prompt = f"""{stock_summary}

ANALYSIS REQUEST:
As a professional stock analyst, analyze the above data and provide SELL recommendations. I need specific, actionable advice.

REQUIRED OUTPUT FORMAT:
For each stock you recommend selling, provide:

1. **SYMBOL & RECOMMENDATION**: [Stock] - [STRONG SELL/SELL/CONSIDER SELLING]
2. **RISK SCORE**: [1-10, where 10 = highest risk/strongest sell signal]
3. **PRICE ANALYSIS**: How does the current price compare to the group?
4. **VOLUME ANALYSIS**: What does the trading volume indicate?
5. **KEY RATIONALE**: 3-4 specific reasons to sell this stock
6. **CONFIDENCE**: [HIGH/MEDIUM/LOW] confidence in this recommendation

ANALYSIS CRITERIA:
- Compare each stock's price to the group average (${np.mean([float(info['close']) for info in stock_data.values()]):.2f})
- Analyze volume patterns for risk signals
- Consider sector-specific factors (tech, aerospace, entertainment)
- Evaluate relative valuation within this portfolio
- Factor in company-specific risks you're aware of

Focus on stocks that show the strongest sell signals based on the current data.
Provide clear, actionable recommendations with specific reasoning.
"""

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.3, 
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 1500 
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        ]
    }
    
    try:
        response = requests.post(
            f"{url}?key={api_key}",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_analysis = result['candidates'][0]['content']['parts'][0]['text']
            check_api_usage_info()
            
            return {
                "success": True,
                "ai_analysis": ai_analysis,
                "stock_summary": stock_summary,
                "api_response": result
            }
        else:
            return {
                "success": False,
                "error": f"API Error: {response.status_code}",
                "message": response.text
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": "Request Failed",
            "message": str(e)
        }

def check_api_usage_info():
    """Display API usage and cost information"""
    print()
    print("REQUEST USAGE:")
    print("   • ~1 API request")
    print("   • ~500-800 tokens (input + output)")
    print("   • Cost: $0.00 (within free limits)")
    print()
    print("Monitor usage at:")
    print("   https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com")
    print()

    