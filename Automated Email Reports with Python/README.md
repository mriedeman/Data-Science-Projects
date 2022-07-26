# Automated Email Reports with Python
## Security
Sensitive information such as emails and passwords have been removed from the repository to protect company data.

## Software

- Python 3.9.12
    - pyodbc
    - email (MIMETEXT, MIMEMultiPart, MIMEBase)
    - smptplib
    - pandas
    - numpy

- Microsoft SQL Server Microsoft SQL Server 2016 13.0.5108.50

- Windows Task Scheduler

## Purpose
Supervisors required several reports on a daily, bi-weekly, or monthly basis, regardless of my presence in the office. To ensure all reports were developed and delivered to the recipients on the correct day, I decided to automate the process. 


# Process Overview

This repository contains several folders, with each folder comprised of files used to develop and release a separate report. The following summarizes the process:

1. A Name_of_Report.py file is used to connect to the SQL Server database, generate the report, and use my email address to to deliver the report.

2. An excel file is produced in the folder which is sent to the desired recipients.

3. The python file path is placed inside a batch file to be used in Windows Task Scheduler. The tasks are scheduled uniquely to the report due date.

4. A name_of_report.ipynb file breaks the file into commented code blocks and details each step. This allows for easier code refactoring when creating future reports.

