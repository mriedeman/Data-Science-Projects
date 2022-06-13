# %%
# imports for SQL data part
import pyodbc
import pandas as pd





# Establishing connection with the DB
cnxn_str = ('Driver={SQL Server};'
                      'Server=SERVER_NAME;'
                      'Database=oneway_processing; reporting_DB;'
                      'Trusted_Connection=yes;')

cnxn = pyodbc.connect(cnxn_str)





# build up our query string
df = pd.read_sql("SELECT r.resNum, s.reqLoc,s.reqEmail, cast(s.reqDate as date)as reqDate, s.pickupLoc as puLoc_A, s.returnLoc as doLoc_A, s.vehClass as Class_A, cast(s.pickupDate  as date) as puDate_A, cast(s.returnDate as date) as doDate_A, cast(s.decisionDate as date)as decisionDate, cast(s.bookDate as date)as bookDate_A,  r.puLoc as puLoc_B, r.retLoc as doLoc_B, r.vehClass as Class_B, cast(r.puDate as date) as puDate_B, cast(r.retDate as date) as doDate_B, cast(r.dateBooked  as date) as bookDate_B, s.processor from oneway_processing.dbo.onewayRequests s JOIN  reportingDB.dbo.departRpt r  ON r.resNum=s.resNum WHERE dateBooked = CAST(GETDATE()-1 AS DATE) and puLoc!=retLoc and bookDate is not null and reqLoc in ('WWR', 'PHX','WDC','SFO','ORL','LAX','EVT','DEN','YVR','YYZ','YYC','YUL','YHZ','ANC') or dateBooked = CAST(GETDATE()-1 AS DATE) and puLoc!=retLoc and bookDate is not null and reqLoc like '[0-9]%' union all SELECT r.resNum, s.reqLoc,s.reqEmail,cast (s.reqDate as date)as reqDate, t.fromLoc as puLoc_A, t.toLoc as doLoc_A, t.vehClass as Class_A, cast(t.puDate as date) as puDate_A, cast(t.arrivalDate as date) as doDate_A,  cast(t.createDate  as date) as decisionDate, cast(s.bookDate as date)as bookDate_A,  puLoc as puLoc_B, retLoc as doLoc_B, r.vehClass as Class_B,cast(r.puDate as date)as puDate_B, cast(retDate as date)as doDate_B,cast(dateBooked as date)as bookDate_B, s.processor from  oneway_processing.dbo.onewayRequests s JOIN reportingDB.dbo.departRpt  r on r.resNum=s.resNum join oneway_processing.dbo.onewayAlternatives t on t.requestID = s.ID WHERE dateBooked = CAST(GETDATE()-1 AS DATE) and puLoc!=retLoc and s.bookDate is not null ORDER BY resNum",cnxn)




# Defining conditional Q/A types  

def Conditions(s):

    if((s['puLoc_A'] != s['puLoc_B'] or s['doLoc_A'] != s['doLoc_B']) and (s['Class_A'] != s['Class_B'])):
         return 'Multiple'
    elif((s['puLoc_A'] != s['puLoc_B'] or s['doLoc_A'] != s['doLoc_B']) and (s['puDate_A'] !=s['puDate_B'] or s['doDate_A'] != s['doDate_B'])):
         return 'Multiple'
    elif((s['puLoc_A'] != s['puLoc_B'] or s['doLoc_A'] != s['doLoc_B']) and (s['decisionDate']!=s['bookDate_B'])):
         return 'Multiple' 
    elif((s['Class_A'] != s['Class_B']) and (s['puDate_A'] !=s['puDate_B'] or s['doDate_A'] != s['doDate_B'])):
         return 'Multiple'    
    elif((s['Class_A'] != s['Class_B']) and (s['decisionDate']!=s['bookDate_B'])):
         return 'Multiple'
    elif((s['puDate_A'] !=s['puDate_B'] or s['doDate_A'] != s['doDate_B']) and (s['decisionDate']!=s['bookDate_B'])):
         return 'Multiple'
    elif(s['decisionDate']!=s['bookDate_B']): 
         return 'Expired M-Code'
    elif(s['puDate_A'] !=s['puDate_B'] or s['doDate_A'] != s['doDate_B']):   
         return 'Dates'
    elif(s['Class_A'] != s['Class_B']):
         return 'Class'
    elif(s['puLoc_A'] != s['puLoc_B'] or s['doLoc_A'] != s['doLoc_B']):
        return 'Loc'
    else:
         return 'N/A'





df['Q/A']= df.apply(Conditions,axis=1)



# Creating excel file to be attached
df.to_excel('onewayQA.xlsx', index = False)
cnxn.close()

# %%
# Imports to send email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import formatdate
from email import encoders

# Text of the email
msg_txt= "**Automated Email**\n\nGentlemen,\n\nHere's the Q/A from yesterday's oneway requests.\n\nMichael"
  

# Stating to and from email addresses
msg = MIMEMultipart()

from_addr = 'MY_EMAIL@OUTLOOK.COM'
to_addr = ['COWORKER_EMAIL@GMAIL.COM']
msg = MIMEMultipart()
msg['From'] = from_addr
msg['To'] = ", ".join(to_addr)
    
msg['Subject'] = "Q/A"
msg.attach(MIMEText(msg_txt))

part = MIMEBase('application', "octet-stream")
part.set_payload(open("onewayQA.xlsx", "rb").read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', 'attachment; filename="onewayQA.xlsx"')
msg.attach(part)

# Sending email via outlook, initializing connection to mail server
server = smtplib.SMTP('smtp-mail.outlook.com', '587')
server.ehlo()  # say hello to the server
server.starttls()

server.login('MYEMAIL@OUTLOOK.COM', 'PASSWORD')

text = msg.as_string()

#Compile email: From, To, Email body
server.sendmail(from_addr, to_addr, text)

server.quit()


