import json

# Configuration variables
user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
search_term = 'facebook'
result_pages_checked = 1

class Crawler(object):
    def __init__(self, user_agent, search_term):
        import mechanize
        from bs4 import BeautifulSoup
        import requests
        import re

        self.mechanize = mechanize
        self.BeautifulSoup = BeautifulSoup
        self.requests = requests
        self.re = re

        # Processed data
        self.links = [] # Will contain all the links found
        self.site_html = '' # The souce code of the site being crawled
        self.emails_found = ''
        self.scrapped_data = {} # Emails found

        # Initialize the browser
        self.browser = self.mechanize.Browser()
        self.browser.set_handle_robots(False)
        self.browser.set_handle_equiv(False)
        self.browser.addheaders = [('User-agent', user_agent)]
        self.browser.open('http://www.google.com/')

        # Querying to google
        self.data = ''
        self.browser.select_form(name='f')
        self.browser.form['q'] = search_term
        self.data = self.browser.submit() # Search result

    def parse_results(self):
        soup = self.BeautifulSoup(self.data.read(),"html5lib")
        for a in soup.select('.r a'):
            url = (a['href']).encode('ascii', 'ignore')
            self.links.append(url)

    def fetch_results(self, result_pages_checked):
        # Starts by fetching the current page obtained when initializing
        self.parse_results()

        # If more than one page of results is wanted
        if result_pages_checked > 1:
            for i in range(1, result_pages_checked):
                self.data = self.browser.follow_link(text='Next')
                self.parse_results()

    def fetch_html(self, url):
        self.site_html = self.requests.get(url)

    def find_email(self):
        self.emails_found = self.re.search(r'[\w\.-]+@[\w\.-]+', self.site_html.text)

    def scrap_emails(self, result_pages_checked):
        self.fetch_results(result_pages_checked)

        for url in self.links:
            self.site_html = ''
            self.fetch_html(url)
            self.find_email()

            if self.emails_found is not None:
                self.scrapped_data[url] = {}
                self.scrapped_data[url]['finds'] = self.emails_found

        return self.scrapped_data




Crawler = Crawler(user_agent, search_term)
# print json.dumps(Crawler.scrap_emails(result_pages_checked))
print Crawler.scrap_emails(result_pages_checked)
