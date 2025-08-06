from textwrap import dedent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for OpenAI API key
if not os.getenv('OPENAI_API_KEY'):
    print("❌ ERROR: OPENAI_API_KEY not found!")
    print("📝 Please set your OpenAI API key in the .env file:")
    print("   OPENAI_API_KEY=your_actual_api_key_here")
    print("   Get your key from: https://platform.openai.com/api-keys")
    exit(1)

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools

finance_agent = Agent(
    model=OpenAIChat(id="gpt-4.1-nano"),
    tools=[
        YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            stock_fundamentals=True,
            historical_prices=True,
            company_info=True,
            company_news=True,
        )
    ],
    instructions=dedent("""\
        You are a seasoned Wall Street analyst with deep expertise in market analysis! 📊

        Follow these steps for comprehensive financial analysis:
        1. Market Overview
           - Latest stock price
           - 52-week high and low
        2. Financial Deep Dive
           - Key metrics (P/E, Market Cap, EPS)
        3. Professional Insights
           - Analyst recommendations breakdown
           - Recent rating changes

        4. Market Context
           - Industry trends and positioning
           - Competitive analysis
           - Market sentiment indicators

        Your reporting style:
        - Begin with an executive summary
        - Use tables for data presentation
        - Include clear section headers
        - Add emoji indicators for trends (📈 📉)
        - Highlight key insights with bullet points
        - Compare metrics to industry averages
        - Include technical term explanations
        - End with a forward-looking analysis

        Risk Disclosure:
        - Always highlight potential risk factors
        - Note market uncertainties
        - Mention relevant regulatory concerns
    """),
    add_datetime_to_instructions=True,
    show_tool_calls=True,
    markdown=True,
)

# Example usage with detailed market analysis request
if __name__ == "__main__":
    print("🚀 Finance Agent Starting...")
    print("📊 Getting Apple (AAPL) market analysis...")
    
    finance_agent.print_response(
        "What's the latest news and financial performance of Apple (AAPL)?", stream=True
    )

# Semiconductor market analysis example
finance_agent.print_response(
    dedent("""\
    Analyze the semiconductor market performance focusing on:
    - NVIDIA (NVDA)
    - AMD (AMD)
    - Intel (INTC)
    - Taiwan Semiconductor (TSM)
    Compare their market positions, growth metrics, and future outlook."""),
    stream=True,
)

# Automotive market analysis example
finance_agent.print_response(
    dedent("""\
    Evaluate the automotive industry's current state:
    - Tesla (TSLA)
    - Ford (F)
    - General Motors (GM)
    - Toyota (TM)
    Include EV transition progress and traditional auto metrics."""),
    stream=True,
) 