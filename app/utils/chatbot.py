import os
import openai
from dotenv import load_dotenv
from app.models.chat import ChatMessage
from app import db

# Load environment variables
load_dotenv()

def get_chatbot_response(user_message, user_id, chat_history_limit=10):
    """
    Get a response from the OpenAI chatbot

    Args:
        user_message: The user's message
        user_id: The user's ID
        chat_history_limit: Number of previous messages to include in context

    Returns:
        str: The chatbot's response
    """
    # Get recent chat history
    chat_history = ChatMessage.query.filter_by(user_id=user_id).order_by(ChatMessage.timestamp.desc()).limit(chat_history_limit).all()
    chat_history = list(reversed(chat_history))  # Reverse to get chronological order

    # Construct messages for the API
    messages = [
        {"role": "system", "content": "You are a specialized financial advisor assistant. You ONLY provide information about financial topics, investment planning, trading, cryptocurrency, and foreign exchange. You are knowledgeable about the Indian stock market and global financial markets.\n\nYou MUST format your responses in a structured manner with the following rules:\n1. Always start with a clear heading using markdown format (# Main Heading)\n2. Use subheadings (## Subheading) to organize information\n3. Use bullet points (* item) for lists of items\n4. Use numbered lists (1. First item) for sequential steps or ranked items\n5. Use bold (**text**) for important terms or concepts\n6. NEVER respond with long paragraphs - always break information into structured sections\n\nIf the user asks about non-financial topics, politely redirect them to financial questions only. You MUST NOT respond to questions unrelated to finance, investing, trading, or economics."}
    ]

    # Add chat history
    for message in chat_history:
        role = "user" if message.is_user else "assistant"
        messages.append({"role": role, "content": message.content})

    # Add the current user message
    messages.append({"role": "user", "content": user_message})

    # Check if API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        # Save the user message to the database
        user_chat_message = ChatMessage(content=user_message, is_user=True, user_id=user_id)
        db.session.add(user_chat_message)

        # Create a structured mock response when no API key is available
        bot_response = "# Financial Assistant\n\nI'm a specialized financial assistant that can help with investment advice, stock information, and financial planning. Please add your OpenAI API key to the .env file to enable my full capabilities.\n"

        # Based on user message, provide some static structured responses
        if "stock" in user_message.lower() or "invest" in user_message.lower():
            bot_response += "\n## Stock Investment Tips\n\n* **Diversification:** Spread investments across large-cap, mid-cap, and small-cap stocks\n* **Key Indices:** Track Nifty 50 and Sensex for market performance\n* **Research:** Always conduct fundamental and technical analysis before investing\n* **Time Horizon:** Consider long-term investment for better returns"
        elif "mutual fund" in user_message.lower() or "sip" in user_message.lower():
            bot_response += "\n## Mutual Fund Investment\n\n1. **SIP Benefits:**\n   * Disciplined investing approach\n   * Rupee cost averaging\n   * Power of compounding\n2. **Fund Categories:**\n   * Equity funds - Higher risk, higher returns\n   * Debt funds - Lower risk, stable returns\n   * Hybrid funds - Balanced approach"
        elif "portfolio" in user_message.lower():
            bot_response += "\n## Portfolio Management\n\n* **Asset Allocation:**\n  1. Stocks: 40-60% (growth)\n  2. Mutual Funds: 20-30% (diversification)\n  3. Bonds: 10-20% (stability)\n  4. Cash: 5-10% (liquidity)\n* **Risk Management:** Align allocation with your risk tolerance\n* **Regular Rebalancing:** Review portfolio quarterly"
        elif "crypto" in user_message.lower() or "bitcoin" in user_message.lower():
            bot_response += "\n## Cryptocurrency Investing\n\n* **High Volatility:** Be prepared for significant price swings\n* **Research:** Understand blockchain technology and use cases\n* **Allocation:** Limit to 5-10% of total portfolio\n* **Security:** Use hardware wallets for long-term storage"
        elif "forex" in user_message.lower() or "currency" in user_message.lower():
            bot_response += "\n## Foreign Exchange Markets\n\n* **Major Pairs:** EUR/USD, USD/JPY, GBP/USD have highest liquidity\n* **Trading Hours:** 24/5 market with varying volatility\n* **Risk Management:** Always use stop-loss orders\n* **Economic Indicators:** Follow central bank decisions and economic data releases"
        else:
            bot_response += "\n## Investment Principles\n\n1. **Start Early:** Benefit from compound interest\n2. **Regular Investing:** Consistency beats timing the market\n3. **Diversification:** Spread risk across asset classes\n4. **Research:** Make informed decisions based on data\n5. **Long-term View:** Focus on long-term goals rather than short-term fluctuations"

        # Save the bot response to the database
        bot_chat_message = ChatMessage(content=bot_response, is_user=False, user_id=user_id)
        db.session.add(bot_chat_message)
        db.session.commit()

        return bot_response

    try:
        # Set the API key
        openai.api_key = api_key

        # Call the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can change this to a different model if needed
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )

        # Format the response to ensure it's structured
        raw_response = response.choices[0].message['content']

        # Check if the response already has headings (starts with #)
        if not any(line.strip().startswith('#') for line in raw_response.split('\n')):
            # Add structure to the response if it doesn't have headings
            bot_response = "# Financial Advice\n\n" + raw_response
        else:
            bot_response = raw_response

        # Save the user message to the database
        user_chat_message = ChatMessage(content=user_message, is_user=True, user_id=user_id)
        db.session.add(user_chat_message)

        # Save the bot response to the database
        bot_chat_message = ChatMessage(content=bot_response, is_user=False, user_id=user_id)
        db.session.add(bot_chat_message)

        db.session.commit()

        return bot_response

    except Exception as e:
        print(f"Error getting chatbot response: {e}")

        # Save the user message to the database
        user_chat_message = ChatMessage(content=user_message, is_user=True, user_id=user_id)
        db.session.add(user_chat_message)

        # Create an error response
        error_response = "# Error Processing Request\n\nI'm sorry, I encountered an error while processing your request.\n\n"

        # Add more specific error messages based on the exception
        if "api_key" in str(e).lower():
            error_response += "## Issue\n* Please make sure you've added your OpenAI API key to the .env file.\n\n## Solution\n1. Edit the .env file\n2. Add your API key: `OPENAI_API_KEY=your_key_here`\n3. Restart the application"
        elif "timeout" in str(e).lower() or "connection" in str(e).lower():
            error_response += "## Connection Issue\n* There seems to be a connection problem\n\n## Troubleshooting\n1. Check your internet connection\n2. Verify the OpenAI API is accessible\n3. Try again in a few moments"
        else:
            error_response += "## Recommendation\n* Please try again later\n* If the issue persists, contact support"

        # Save the error response to the database
        bot_chat_message = ChatMessage(content=error_response, is_user=False, user_id=user_id)
        db.session.add(bot_chat_message)

        try:
            db.session.commit()
        except Exception as db_error:
            print(f"Error saving chat messages: {db_error}")
            db.session.rollback()

        return error_response
