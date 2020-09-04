# Email-Extractor
Email Extractor is use to scrape the urls in **google spreadsheet** and extract emails, put them back to the spreadsheet.
It need to be call like `python email_extractor.py <spreadsheet_title> <worksheet_title> <url_col_number> <email_col_number> <service_account_json>` below:  
`python email_extractor backlinks http://google.com 1 5 account.json`