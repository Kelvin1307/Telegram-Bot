import os
import re
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"]=os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_TRACING_V2"]="true"
groq_api_key=os.getenv("GROQ_API_KEY")

def setup_llm_chain(topic="technology"):
    prompt=ChatPromptTemplate.from_messages([
        ("system","Act as a hackathon mentor and help me to get the following details on my idea.Summarize the following idea/topic with a structured format that includes:Catchy Name/Title – Give a creative, relevant, and engaging name to the idea.Problem Statement – Describe the key problem(s) the idea addresses.Solution/Idea Abstract – Explain the core idea or solution in a concise and understandable way.Innovated From – Mention any existing technologies, concepts, or inspirations this idea was derived or innovated from.Design Explanation – Describe how the idea is designed or implemented, covering core mechanisms, technologies used, and user interaction (if applicable).Advantages/Benefits – Highlight the practical benefits, improvements over existing solutions, and potential impact.Further Research/Reference Links – Provide at least 2–3 credible and relevant links (e.g., academic articles, technical blogs, white papers, or official documentation) for deeper understanding or related research.The entire summary must be under 4000 characters. The tone should be professional, concise, and suitable for a technical innovation report or project proposal."),
        ("user",f"generate the summary for the idea topic:{topic}")
    ])

    llm=ChatGroq(
        model="deepseek-r1-distill-llama-70b",
        groq_api_key=groq_api_key

    )

    return prompt|llm|StrOutputParser()

async def start(update: Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi, Give me your Idea to refine, like '@T_Kelvin_bot (your idea)' to get your result")

async def generate_idea(update: Update, context:ContextTypes.DEFAULT_TYPE,topic:str):
    await update.message.reply_text(f"Generating the result about {topic}")
    idea=setup_llm_chain(topic).invoke({}).strip()
    await update.message.reply_text(idea)

async def handle_message(update: Update, context:ContextTypes.DEFAULT_TYPE):
    msg=update.message.text
    bot_username= context.bot.username

    if f'@{bot_username}' in msg:
        match=re.search(f'@{bot_username}\\s+(.*)',msg)
        if match and match.group(1).strip():
            await generate_idea(update,context,match.group(1).strip())
        else:
            await update.message.reply_text("Please specify a topic after mentioning me")


def main():
    token=os.getenv("TELEGRAM_API_KEY")
    app=Application.builder().token(token).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ =="__main__":
    main()
