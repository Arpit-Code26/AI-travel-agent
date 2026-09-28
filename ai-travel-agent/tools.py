import os
import markdown
from langchain_core.tools import tool
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()

@tool
def search_flights_and_hotels(query: str) -> str:
    """Searches for flights and hotels based on the user query."""
    params = {
        "engine": "google",
        "q": query,
        "api_key": os.environ.get("SERPAPI_API_KEY")
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return str(results.get("organic_results", "No results found."))

@tool
def send_itinerary_email(to_email: str, itinerary_text: str) -> str:
    """Sends the travel itinerary via email. Accepts plain markdown text."""
    # Convert plain markdown syntax into valid HTML
    html_body = markdown.markdown(itinerary_text)
    
    # Wrap in standard body styling so Gmail displays clean fonts and spacing
    full_email_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #222; max-width: 650px; margin: 0 auto; padding: 20px;">
        {html_body}
    </body>
    </html>
    """

    message = Mail(
        from_email='arpitnainwal3@gmail.com',
        to_emails=to_email,
        subject='Your AI Travel Itinerary',
        html_content=full_email_html
    )
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        sg.send(message)
        return "Email sent successfully."
    except Exception as e:
        return f"Failed to send email: {str(e)}"