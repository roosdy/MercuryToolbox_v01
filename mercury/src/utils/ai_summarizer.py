# src/utils/ai_summarizer.py
from openai import OpenAI
from dotenv import load_dotenv
import os


# Load environment variables
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_email(email_content):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant who summarizes email key content in brisk bullet points for ease of readability, and disregards pleasantries."
                },
                {
                    "role": "user",
                    "content": f"Summarize the following email:\n\n{email_content}"
                }
            ],
            temperature=1,
            max_tokens=4000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in AI summarization: {e}")
        return "Unable to summarize email content."