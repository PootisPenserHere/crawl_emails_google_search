import json

# Configuration variables
user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
search_term = 'email'
result_pages_checked = 3

# To randomize the reading time of the result pages
minimum_time_per_page = 10
maximum_time_per_page = 18

class Crawler(object):
    def __init__(self, user_agent, search_term, minimum_time_per_page, maximum_time_per_page):
        import mechanize
        from bs4 import BeautifulSoup
        import requests
        import re
        from random import SystemRandom
        from time import sleep

        self.mechanize = mechanize
        self.BeautifulSoup = BeautifulSoup
        self.requests = requests
        self.re = re
        self.SystemRandom = SystemRandom
        self.sleep = sleep

        # Configuration perams
        self.minimum_time_per_page = minimum_time_per_page
        self.maximum_time_per_page = maximum_time_per_page

        # Processed data
        self.links = [] # Will contain all the links found
        self.site_html = '' # The souce code of the site being crawled
        self.emails_found = '' # Emails found in the site being currently scraped
        self.scrapped_data = {} # Emails found
        self.random_wait_time = '' # Time till the next query to google search
        self.total_result_pages_found = 1
        self.timeoutToFetchHtml = 5 # In seconds

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

        # Initializing the random number generator
        self.sr = self.SystemRandom()

        # Request headers
        self.headers = {
            'User-Agent': user_agent
        }

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
                # Sleeps for a random period of time
                self.random_number()
                self.sleep(self.random_wait_time)

                try:
                  self.data = self.browser.follow_link(text='Next')
                  self.parse_results()
                  self.total_result_pages_found += 1
                except (self.mechanize.HTTPError,self.mechanize.URLError, self.mechanize.LinkNotFoundError) as e:
                  return False

    def fetch_html(self, url):
        self.sleep(0.01)
        try:
            self.site_html = self.requests.get(url, headers=self.headers, timeout=self.timeoutToFetchHtml)
            return True
        except self.requests.exceptions.RequestException as e:
            print url
            return False

    def find_email(self):
        self.emails_found = self.re.search(r'[\w\.-]+@[\w\.-]+', self.site_html.text)

    def random_number(self):
        number = self.sr.choice(xrange(self.minimum_time_per_page, self.maximum_time_per_page))
        self.random_wait_time = number

    def scrap_emails(self, result_pages_checked):
        self.fetch_results(result_pages_checked)

        for url in self.links:
            self.site_html = ''
            if self.fetch_html(url) is True:
                self.find_email()

                if self.emails_found is not None:
                    self.emails_found = self.emails_found.group(0)
                    self.emails_found = self.emails_found.encode('ascii', 'ignore')
                    self.scrapped_data[url] = {}
                    self.scrapped_data[url]['finds'] = self.emails_found

        self.scrapped_data['pages_found'] = {}
        #self.scrapped_data['pages_found']['desired'] =
        self.scrapped_data['pages_found']['found'] = self.total_result_pages_found

        return self.scrapped_data

Crawler = Crawler(user_agent, search_term, minimum_time_per_page, maximum_time_per_page)
print json.dumps(Crawler.scrap_emails(result_pages_checked))
