import logging
import gspread, pandas as pd
from telegram import Update
import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

load_dotenv()

token =  os.getenv('TELEGRAM_TOKEN')

# Set up basic logging to see errors in the console
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="I'm a bot, please talk to me!"
    )

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gc = gspread.service_account(filename="sheetscripts.json")
    sh = gc.open(title="Script")
    worksheet = sh.get_worksheet(0)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data=data)
    total_revenue = df["Amount Due"].sum()
    paid = df["Amount Due"][df["Status"] == "Paid"].sum()
    unpaid = df["Amount Due"][df["Status"] == "Unpaid"].sum()
    reminded = len(df["Reminded"][df["Reminded"] == "Yes"])

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Hello here is your weekly report: \
                   \nTotal revenue: {total_revenue} \
                   \nAmount paid: {paid} \
                   \nAmount unpaid: {unpaid} \
                   \nTotal of reminded: {reminded}"
    )

# Function to echo back messages
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=update.message.text
    )

if __name__ == '__main__':
    # Initialize the application with your bot's token
    application = ApplicationBuilder().token(token).build()
    
    # Register handlers
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    report_handler = CommandHandler('report', report)
    
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(report_handler)
    # Run the bot until you press Ctrl-C
    application.run_polling()
