import logging
import gspread, pandas as pd
from telegram import Update
import os
from datetime import datetime
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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

async def reminded(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gc = gspread.service_account(filename="sheetscripts.json")
    sh = gc.open(title="Script")
    worksheet = sh.get_worksheet(0)
    data = worksheet.get_all_records()
    found =  False
    for index, client in enumerate(data):
        if client['Client name'].lower() == ' '.join(context.args).lower():
            found = True
            if client['Reminded'] != 'Yes':
                worksheet.update_cell(row=index + 2, col=5, value='Yes')
                await context.bot.send_message(
                    chat_id= update.effective_chat.id,
                    text=f'{' '.join(context.args)} is reminded'
                )
                break
            else:
                await context.bot.send_message(
                    chat_id= update.effective_chat.id,
                    text=f'{' '.join(context.args)} is already reminded'
                )
    if not found:
         await context.bot.send_message(
                    chat_id= update.effective_chat.id,
                    text=f'{' '.join(context.args)} is not found'
                )

async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gc = gspread.service_account(filename="sheetscripts.json")
    sh = gc.open(title="Script")
    worksheet = sh.get_worksheet(0)
    data = worksheet.get_all_records()
    found =  False
    for index, client in enumerate(data):
        if client['Client name'].lower() == ' '.join(context.args).lower():
            found = True
            if client['Status'] != 'Paid':
                worksheet.update_cell(row=index + 2, col=6, value='Paid')
                await context.bot.send_message(
                    chat_id= update.effective_chat.id,
                    text=f'{' '.join(context.args)} status is now Paid'
                )
                break
            else:
                await context.bot.send_message(
                    chat_id= update.effective_chat.id,
                    text=f'{' '.join(context.args)} status is already Paid'
                )
    if not found:
         await context.bot.send_message(
                    chat_id= update.effective_chat.id,
                    text=f'{' '.join(context.args)} is not found'
                )

async def invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gc = gspread.service_account(filename="sheetscripts.json")
    sh = gc.open(title="Script")
    worksheet = sh.get_worksheet(0)
    data = worksheet.get_all_records()

    found = False
    for client in data:
        if client['Client name'].lower() == ' '.join(context.args).lower():
            found = True
            doc = SimpleDocTemplate(f"{client['Client name']}_invoice.pdf", pagesize=letter)
            styles = getSampleStyleSheet()

            elements = []

            elements.append(Paragraph("Report PDF", styles['Title']))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"Business: FabiShop", styles['Normal']))
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(f"Invoice number: {str(datetime.today().strftime('%Y%m%d')) + client['Client name']}", styles['Normal']))
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(f"Name: {' '.join(context.args)}", styles['Normal']))
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(f"Email: {client["Email"]}", styles['Normal']))
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(f"Amount Due: {client["Amount Due"]}", styles['Normal']))
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(f"Due Date: {client["Due Date"]}", styles['Normal']))
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(f"Status: {client["Status"]}", styles['Normal']))

            doc.build(elements)

            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document= open(f"{client['Client name']}_invoice.pdf", "rb")
            )
            break
    
    if not found:
         await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"{' '.join(context.args)} not found"
            )

if __name__ == '__main__':
    # Initialize the application with your bot's token
    application = ApplicationBuilder().token(token).build()
    
    # Register handlers
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    report_handler = CommandHandler('report', report)
    reminded_handler = CommandHandler('reminded', reminded)
    paid_handler = CommandHandler('paid', paid)
    invoice_handler  = CommandHandler('invoice', invoice)

    
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(report_handler)
    application.add_handler(reminded_handler)
    application.add_handler(paid_handler)
    application.add_handler(invoice_handler)


    # Run the bot until you press Ctrl-C
    application.run_polling()
