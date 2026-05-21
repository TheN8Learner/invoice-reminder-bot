import gspread, pandas as pd
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
import schedule, time

load_dotenv()
file = os.getenv('file')
email = os.getenv('email')
password = os.getenv('password')

def send_email(to, client_name, total_revenue, unpaid, paid, overdue):
    msg = MIMEText(f"Hi {client_name} there is ur weekly report: \
                    \nTotal revenue: {total_revenue} \
                    \nUnpaid amount: {unpaid} \
                    \nPaid amount: {paid} \
                    \nOverdue of reminded: {overdue}")
    
    msg['Subject'] = 'Weekly report'
    msg['From'] = email
    msg['to'] = to

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(email, password)
        server.sendmail(email, to, msg.as_string())

gc = gspread.service_account(filename=file)

sh = gc.open('Script')

worksheet = sh.get_worksheet(0)
data = worksheet.get_all_records()

df = pd.DataFrame(data=data)

total_revenue = df['Amount Due'].sum()
unpaid = df[df['Status'] == 'Unpaid']['Amount Due'].sum()
paid = df[df['Status'] == 'Paid']['Amount Due'].sum()
overdue_count = len(df[df['Reminded'] == 'Yes'])

print("Total revenue: ", total_revenue)
print("Unpaid: ", unpaid)
print("Paid: ", paid)
print("overdue count: ", overdue_count)

schedule.every().thursday.at("14:20").do(send_email, to=email, client_name='Boss', total_revenue=total_revenue, unpaid=unpaid, paid=paid, overdue=overdue_count)

while True:
    schedule.run_pending()
    time.sleep(1)

