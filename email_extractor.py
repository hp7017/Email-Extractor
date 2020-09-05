from bs4 import BeautifulSoup
import requests
import re

class Extractor:

	def __init__(self, website):
		self.website = website
		self.page = None

	def crawl(self):
		context = {}
		try:
			r = requests.get(self.website, timeout=8)
			r.raise_for_status()
		except Exception as e:
			return {
				'errors': {
					'response_code': r.status_code if 'r' in locals() else None,
					'exception': type(e).__name__
				}
			}
		self.page = BeautifulSoup(r.text, 'lxml')
		domain = re.findall(r'http[s]*://[\w.]*', self.website)
		if domain:
			domain = domain[0]
			context['domain'] = domain
		else:
			context.update({
				'errors': {
					'domain': 'Could not find'
				}
			})
			return context
		emails = re.findall(r'[a-zA-Z0-9]+@[a-zA-Z0-9]+[.][a-zA-Z0-9]*[a-zA-Z0-9.]*', self.page.get_text())
		if emails:
			context['emails'] = emails
		contact = [a.attrs['href'] for a in self.page.findAll('a') if 'href' in a.attrs if re.search(r'[/]contact[\w]*', a.attrs['href'])]
		if contact:
			contact = contact[0]
			context['contact'] = contact
		else:
			context.update({
				'errors': {
					'contact':'contact could not find'
					},
				})
			return context
		try:
			r = requests.get(f'{domain}{contact}', timeout=8)
		except Exception as e:
			context.update({
				'errors': {
					'contact_page_response_code': r.status_code if 'r' in locals() else None,
					'exception': type(e).__name__
				},
			})
			return context
		bsobj = BeautifulSoup(r.text, 'lxml')
		emails = re.findall(r'[a-zA-Z0-9]+@[a-zA-Z0-9]+[.][a-zA-Z0-9]*[a-zA-Z0-9.]*', bsobj.get_text())
		if emails:
			if 'emails' in context:
				context['emails'].extend(emails)
			else:
				context['emails'] = emails
		return context

def alpha_of(n):	
	string = ""
	while n > 0:
		n, remainder = divmod(n - 1, 26)
		string = chr(65 + remainder) + string
	return string

def run():
	import sys
	try:
		file, sh_title, wsh_title, url_col_number, email_col_num, auth_json = sys.argv
	except ValueError as e:
		print('It need to be call like python email_extractor.py <spreadsheet_title> <worksheet_title> <url_col_number> <email_col_number> <service_account_json> below:\n-> python email_extractor backlinks http://google.com 1 5 account.json')
		sys.exit(e)
	import gspread
	gc = gspread.service_account(filename=auth_json)
	print('service_account has been created sucessfully')
	sh = gc.open(sh_title)
	print('sheet opened')
	wsh = sh.worksheet(wsh_title)
	print('worksheet opened')
	urls = wsh.col_values(url_col_number)
	row = 2
	for url in urls[1:]:
		print(url, end=' ')
		crawled_page = Extractor('http://'+url).crawl()
		if 'emails' in crawled_page:
			wsh.update_cell(row, email_col_num, '\n'.join(crawled_page['emails']))
			print('worksheet updated')
		else:
			print(crawled_page)
		row += 1

if __name__ == '__main__':
	run()