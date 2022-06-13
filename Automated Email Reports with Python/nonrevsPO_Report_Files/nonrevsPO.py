# %%
# imports for SQL data part

import pandas as pd
import numpy as np


# %%
# imports for sending email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# %%
import pyodbc 
conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=SERVER_NAME;'                
                      'Database=purchase_order;'
                      'Trusted_Connection=yes;')

# %%
cursor = conn.cursor()
query= "with records as (select f.vehNum,vehVIN, f.vehYear, f.vehStatus, f.idleDate , f.vehLoc, requestDate,row_number() over (partition by[VehVIN] order by requestDate desc ) as sr from purchase_order.dbo.fleet f left join purchase_order.dbo.poData p on f.vehNum = p.vehNum where f.vehStatus = 'N') Select vehLoc,vehNum,cast(idleDate as date) as nonrevDate,cast(requestDate as date) as latestPO, DATEDIFF(DAY,   idleDate, GETDATE()) as idleDays,isnull(DATEDIFF(DAY,requestDate, GETDATE()),null) as days_sincePO from records where sr=1  order by days_sincePO desc, idleDays, vehLoc "
results = cursor.execute(query).fetchall()

df=pd.read_sql_query(query,conn)

# %%
df['days_sincePO'] = np.where(df['days_sincePO'] >= df['idleDays'], df['idleDays'],df['days_sincePO'] )

# %%
df=df.sort_values (by='days_sincePO',ascending=False)

# %%
df.to_excel('nonrevsPO.xlsx', index = False)
conn.close()

# %%
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import formatdate
from email import encoders

msg_txt= "**Automated Email**\n\nGentlemen,\n\nHere is the weekly report for purchase orders made for vehicles in non-rev.\n\nMichael"
  

msg = MIMEMultipart()

from_addr = 'MY_EMAIL@OUTLOOK.COM'
to_addr = ['COWORKER_EMAIL@OUTLOOK.COM']
msg = MIMEMultipart()
msg['From'] = from_addr
msg['To'] = ", ".join(to_addr)
    
msg['Subject'] = "Non-Rev Purchase Orders"
msg.attach(MIMEText(msg_txt))

part = MIMEBase('application', "octet-stream")
part.set_payload(open("nonrevsPO.xlsx", "rb").read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', 'attachment; filename="nonrevsPO.xlsx"')
msg.attach(part)

# we will send via outlook, first we initialise connection to mail server
server = smtplib.SMTP('smtp-mail.outlook.com', '587')
server.ehlo()  # say hello to the server
server.starttls()

server.login('MY_EMAIL@OUTLOOK.COM', 'PASSWORD')

text = msg.as_string()

#Compile email: From, To, Email body
server.sendmail(from_addr, to_addr, text)
  
    
server.quit()

# %%



