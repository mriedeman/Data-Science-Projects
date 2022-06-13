# %% [markdown]
# # Daily Reservation Report

# %%
#connect to database
import pyodbc 

#build report
import pandas as pd
import numpy as np

# create and send email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import formatdate
from email import encoders
import smtplib



# %%
# connect to database

try: 
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=SERVER_NAME;'                
                      'Database=reportingdb;'
                      'Trusted_Connection=yes;')
    print("Successfully connected to the database")
except: print("Did not connect to  the database")

# %%
# Load into Pandas

# --  from departRpt table: lastName, resNum, puDate, puLoc, vehClass, retDate, retLoc, bookingLoc, dateBooked
# -- from wwr_resdic table: emplNum, 
# --,departRpt.tourOp,   departRpt.cancelDate,   departRpt.raNum

cursor = conn.cursor()
query = """


SELECT        departRpt.lastName AS CUSTOMER, departRpt.resNum AS "RESERVATION #" ,
              departRpt.puDate AS "PICK-UP DATE", departRpt.puLoc AS "PICK-UP LOCATION",
			  departRpt.vehClass AS "VEHICLE CLASS", departRpt.retDate AS "RETURN DATE",
			  departRpt.retLoc AS "RETURN LOCATION", departRpt.bookingLoc AS "BOOKING LOCATION",
			  departRpt.dateBooked AS "DATE BOOKED" ,wwr_resdisc.emplNum AS "BOOKED BY" 
			  

FROM            departRpt LEFT OUTER JOIN
                         wwr_resdisc ON departRpt.resNum = wwr_resdisc.resNum
WHERE        departRpt.dateBooked = CAST(GETDATE() - 1 AS DATE)

"""
# results = cursor.execute(query).fetchall()

df=pd.read_sql_query(query,conn)


df.to_excel('Daily_Reservation_Report.xlsx', index = False)
conn.close()

# %%


# %%
# send email

#create multipart email object
email = MIMEMultipart()

sender = 'MY_OUTLOOK_EMAIL@COMPANY_NAME.COM'
recipients = ['EXAMPLE_EMAIL@GMAIL.COM', 'EXAMPLE_EMAIL@OUTLOOK.COM']

email_txt= "**Automated Email**\n\nGentlemen,\n\nHere is the daily reservation report.\n\nMichael"

email['From'] = sender
email['To'] = ", ".join(recipients)
email['Subject'] = "Daily Reservation Report"

email.attach(MIMEText(email_txt))

# https://kb.iu.edu/d/agtj Explain "application/octet_stream"
# A MIME attachment with the content type "application/octet-stream" is a binary file. 
# Typically, it will be an application or a document that must be opened in an application, such as a spreadsheet or word processor.
mimeattachment = MIMEBase('application', "octet-stream")

#Set the entire message object’s payload to payload. It is the client’s responsibility to ensure the payload invariants. Optional charset sets the message’s default character set; see set_charset() for details.

# This is a legacy method. On the EmailMessage class its functionality is replaced by set_content().
mimeattachment.set_payload(open("Daily_Reservation_Report.xlsx", "rb").read())


# Encode file in ASCII characters to send by email
encoders.encode_base64(mimeattachment)


mimeattachment.add_header('Content-Disposition', 'attachment; filename="Daily_Reservation_Report.xlsx"')
email.attach(mimeattachment)
#initialise connection to outlook mail server
server = smtplib.SMTP('smtp-mail.outlook.com', '587')

#hostname to identify itself
server.ehlo()  

#puts the connection to the SMTP server into TLS mode.

#TLS :

# Transport Layer Security (TLS) encrypts data sent over the Internet to ensure that 
# eavesdroppers and hackers are unable to see what you transmit which is particularly
#  useful for private and sensitive information such as passwords, credit card numbers,
#  and personal correspondence.

server.starttls()

#Log in on an SMTP server that requires authentication.
server.login('MY_OUTLOOK_EMAIL@COMPANY_NAME.COM', 'PASSWORD')

text = email.as_string()

#Compile email: From, To, Email body
server.sendmail(sender, recipients, text)
  
    
server.quit()

# %%



