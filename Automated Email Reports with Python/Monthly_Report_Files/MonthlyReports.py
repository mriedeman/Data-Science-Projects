# %%
# imports for SQL data part

import pandas as pd

# %%
# imports for sending email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


# %%
import pyodbc 
conn1 = pyodbc.connect('Driver={SQL Server};'
                      'Server=SERVER_NAME;'                
                      'Database=purchase_order;'
                      'Trusted_Connection=yes;')

cursor = conn1.cursor()
query1= "select * from [purchase_order].[dbo].[poData] WHERE DATEPART(m, requestDate) = DATEPART(m, DATEADD(m, -1, getdate())) AND DATEPART(yyyy, requestDate) = DATEPART(yyyy, DATEADD(m, -1, getdate())) order by requestDate;"

results = cursor.execute(query1).fetchall()

df1=pd.read_sql_query(query1,conn1)

df1.to_excel('purchase_order.xlsx', index = False)

conn1.close()


# %%

conn2 = pyodbc.connect('Driver={SQL Server};'
                      'Server=SERVER_NAME;'                
                      'Database=oneway_processing;'
                      'Trusted_Connection=yes;')

cursor = conn2.cursor()
query2= "select * from [oneway_processing].[dbo].[onewayRequests] where DATEPART(m, reqDate) = DATEPART(m, DATEADD(m, -1, getdate())) AND DATEPART(yyyy, reqDate) = DATEPART(yyyy, DATEADD(m, -1, getdate())) order by reqDate;"

results = cursor.execute(query2).fetchall()

df2=pd.read_sql_query(query2,conn2)

df2.to_excel('oneway_requests.xlsx', index = False)

conn2.close()

# %%

conn3 = pyodbc.connect('Driver={SQL Server};'
                      'Server=SERVER_NAME;'                
                      'Database=travelers_assistance;'
                      'Trusted_Connection=yes;')

cursor = conn3.cursor()
query3= "SELECT * FROM [travelers_assistance].[DBO].[crLogV2] WHERE DATEPART(m, logDateTime) = DATEPART(m, DATEADD(m, -1, getdate())) AND DATEPART(yyyy, logDateTime) = DATEPART(yyyy, DATEADD(m, -1, getdate()));"

results = cursor.execute(query3).fetchall()

df3=pd.read_sql_query(query3,conn3)

df3.to_excel('CR_logs.xlsx', index = False)

conn3.close()

# %%
conn4 = pyodbc.connect('Driver={SQL Server};'
                      'Server=SERVER_NAME;'                
                      'Database=travelers_assistance;'
                      'Trusted_Connection=yes;')

cursor = conn4.cursor()
query4= "SELECT * FROM [travelers_assistance].[DBO].[taAssistanceLogsV2] WHERE DATEPART(m, logDateTime) = DATEPART(m, DATEADD(m, -1, getdate())) AND DATEPART(yyyy, logDateTime) = DATEPART(yyyy, DATEADD(m, -1, getdate()));"

results = cursor.execute(query4).fetchall()

df4=pd.read_sql_query(query4,conn4)

df4.to_excel('TA_logs.xlsx', index = False)

conn4.close()

# %%
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import formatdate
from email import encoders


    
msg_txt= "**Automated Email**\n\nHey Joey,\n\nHere are the monthly reports for last month.\n\nBest,\nMichael"
  

msg = MIMEMultipart()
    
msg['Subject'] = "Monthly Reports"
msg.attach(MIMEText(msg_txt))# add text contents


part1 = MIMEBase('application', "octet-stream")
part1.set_payload(open("purchase_order.xlsx", "rb").read())
encoders.encode_base64(part1)
part1.add_header('Content-Disposition', 'attachment; filename="purchase_order.xlsx"')
msg.attach(part1)

part2 = MIMEBase('application', "octet-stream")
part2.set_payload(open("oneway_requests.xlsx", "rb").read())
encoders.encode_base64(part2)
part2.add_header('Content-Disposition', 'attachment; filename="oneway_requests.xlsx"')
msg.attach(part2)

part3 = MIMEBase('application', "octet-stream")
part3.set_payload(open("CR_logs.xlsx", "rb").read())
encoders.encode_base64(part3)
part3.add_header('Content-Disposition', 'attachment; filename="CR_logs.xlsx"')
msg.attach(part3)

part4 = MIMEBase('application', "octet-stream")
part4.set_payload(open("TA_logs.xlsx", "rb").read())
encoders.encode_base64(part4)
part4.add_header('Content-Disposition', 'attachment; filename="TA_logs.xlsx"')
msg.attach(part4)


# we will send via outlook, first we initialise connection to mail server
smtp = smtplib.SMTP('smtp-mail.outlook.com', '587')
smtp.ehlo()  # say hello to the server
smtp.starttls()

# change these as per use
smtp.login('MYEMAIL@OUTLOOK.COM', 'PASSWORD')

# send email to our boss
smtp.sendmail('MYEMAIL@OUTLOOK.COM', 'COWORKER@OUTLOOK.COM', msg.as_string())  # 'jreed@cruiseamerica.com'
    
smtp.quit()

# %%



