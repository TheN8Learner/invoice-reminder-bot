import smtplib, gspread, pandas as pd
from dotenv import load_dotenv
from email.mime.text import MIMEText
from datetime import datetime

def send_emails(to, receiver_name, total_revenue, paid, unpaid, reminded):
    msg = MIMEText(f"Hello {receiver_name} here is your weekly report: \
                   \nTotal revenue: {total_revenue} \
                   \nAmount paid: {paid} \
                   \nAmount unpaid: {unpaid} \
                   \nTotal of reminded: {reminded}")
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login("dalphaoumar21000@gmail.com", "brxtjpjmfjpbfmkv")
        server.sendmail("dalphaoumar21000@gmail.com",to, msg.as_string())
        print(f"Message sent to {to} successfully")

gc = gspread.service_account(filename="sheetscripts.json")

sh = gc.open('Script')

worksheet = sh.get_worksheet(0)

data = worksheet.get_all_records()

df = pd.DataFrame(data=data)

total_revenue = df["Amount Due"].sum()
paid = df["Amount Due"][df["Status"] == "Paid"].sum()
unpaid = df["Amount Due"][df["Status"] == "Unpaid"].sum()
reminded = len(df["Reminded"][df["Reminded"] == "Yes"])
print(total_revenue)
print(paid)
print(unpaid)
print(reminded)

today = datetime.today().date()
row = 2

for client in data:
    due_date = datetime.strptime(client['Due Date'], '%Y-%m-%d').date()
    is_overdue = today > due_date
    already_reminded = client['Reminded'] == 'Yes'
    
    if is_overdue and not already_reminded:
        try:
            send_emails(client['Email'], "Boss", total_revenue, paid, unpaid, reminded)
            print(f"Reminder sent to {client['Client name']}")
            worksheet.update_cell(row=row, col=5, value='Yes')
        except Exception as e:
             print(f"Failed to send to {client['Client name']}: {e}")
    row += 1




















# import gspread, pandas as pd
# import os
# from dotenv import load_dotenv
# import smtplib
# from email.mime.text import MIMEText

# import json

# credentials = os.getenv('GOOGLE_CREDENTIALS')
# with open('sheetscripts.json', 'w') as f:
#     f.write(credentials)

# load_dotenv()
# email = os.getenv('email')
# password = os.getenv('password')

# def send_email(to, client_name, total_revenue, unpaid, paid, overdue):
#     msg = MIMEText(f"Hi {client_name} there is ur weekly report: \
#                     \nTotal revenue: {total_revenue} \
#                     \nUnpaid amount: {unpaid} \
#                     \nPaid amount: {paid} \
#                     \nOverdue of reminded: {overdue}")
    
#     msg['Subject'] = 'Weekly report'
#     msg['From'] = email
#     msg['to'] = to

#     with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
#         server.login(email, password)
#         server.sendmail(email, to, msg.as_string())

# gc = gspread.service_account(filename='sheetscripts.json')

# sh = gc.open('Script')

# worksheet = sh.get_worksheet(0)
# data = worksheet.get_all_records()

# df = pd.DataFrame(data=data)

# total_revenue = df['Amount Due'].sum()
# unpaid = df[df['Status'] == 'Unpaid']['Amount Due'].sum()
# paid = df[df['Status'] == 'Paid']['Amount Due'].sum()
# overdue_count = len(df[df['Reminded'] == 'Yes'])

# print("Total revenue: ", total_revenue)
# print("Unpaid: ", unpaid)
# print("Paid: ", paid)
# print("overdue count: ", overdue_count)

# send_email(to=email, client_name='Boss', total_revenue=total_revenue, unpaid=unpaid, paid=paid, overdue=overdue_count)



