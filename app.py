import re
import json

# Configuration variables
user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
search_term = 'python'
result_pages_checked = 3

class Crawler(object):
    def __init__(self, user_agent, search_term):
        import mechanize
        from bs4 import BeautifulSoup

        self.mechanize = mechanize
        self.BeautifulSoup = BeautifulSoup

        # Returned data
        self.links = [] # Will contain all the links found

        # Initialize the browser
        self.browser = self.mechanize.Browser()
        self.browser.set_handle_robots(False)
        self.browser.set_handle_equiv(False)
        self.browser.addheaders = [('User-agent', user_agent)]
        self.browser.open('http://www.google.com.mx/')

        # Querying to google
        self.data = ''
        self.browser.select_form(name='f')
        self.browser.form['q'] = search_term
        self.data = self.browser.submit() # Search result

    def parse_results(self):
        soup = self.BeautifulSoup(self.data.read(),"html5lib")
        for a in soup.select('.r a'):
            self.links.append(a['href'])

    def fetch_results(self, result_pages_checked):
        # Starts by fetching the current page obtained when initializing
        self.parse_results()

        # If more than one page of results is wanted
        if result_pages_checked > 1:
            for i in range(1, result_pages_checked):
                self.data = self.browser.follow_link(text='Next')
                self.parse_results()

        return self.links

Crawler = Crawler(user_agent, search_term)
print json.dumps(Crawler.fetch_results(result_pages_checked))
