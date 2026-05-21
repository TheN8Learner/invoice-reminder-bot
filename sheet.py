import gspread
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import os, dotenv


dotenv.load_dotenv()

password = os.getenv('password')
myEmail = os.getenv('email')
myFile = os.getenv('file')

def send_email(to, client_name, amount):
    msg = MIMEText(f"Hi {client_name}, your payment of ${amount} is overdue. Please pay ASAP.")
    msg['Subject'] = 'Payment Reminder'
    msg['From'] = myEmail
    msg['To'] = to

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(myEmail, password)
        server.sendmail(myEmail, to, msg.as_string())


gc = gspread.service_account(filename=myFile)

sh = gc.open(title='Script')

worksheet = sh.get_worksheet(0)

data = worksheet.get_all_records()

today = datetime.today().date()
row = 2

for client in data:
    due_date = datetime.strptime(client['Due Date'], '%Y-%m-%d').date()
    is_overdue = today > due_date
    already_reminded = client['Reminded'] == 'Yes'
    
    if is_overdue and not already_reminded:
        try:
            send_email(
                to=client['Email'],
                client_name=client['Client name'],
                amount=client['Amount Due']
            )
            print(f"Reminder sent to {client['Client name']}")
            worksheet.update_cell(row=row, col=5, value='Yes')
        except Exception as e:
             print(f"Failed to send to {client['Client name']}: {e}")
    row += 1



