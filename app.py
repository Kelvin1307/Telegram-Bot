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
        ("system","Act as a hackathon mentor and help me refine my idea. Ask me targeted questions to uncover weaknesses, strengths, and execution steps. Then, summarize the idea in a clear pitch format, including: Problem Statement (Who suffers? Why is it urgent?)Solution (Tech stack, innovation, MVP scope)Target Users (Specific demographics/use cases)Feasibility Check (Resources needed, risks, timeline)Judging Appeal (Why would this win? Metrics for success)"),
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
    await update.message.reply_text(f"Generating an idea about {topic}")
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
