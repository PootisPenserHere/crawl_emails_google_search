""" crawl_emails_google_search, retrival of emails through google search
Copyright (C) 2018  Jose Pablo Domingo Aramburo Sanchez

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, version 3 of the
License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from flask import Flask
from flask import jsonify
import json

app = Flask(__name__)

# Configuration variables
user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
search_term = 'email'
result_pages_checked = 3

# To randomize the reading time of the result pages
minimum_time_per_page = 3
maximum_time_per_page = 6

class Crawler(object):
    def __init__(self, user_agent, search_term, minimum_time_per_page, maximum_time_per_page, result_pages_checked):
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
        self.emails_found = [] # Emails found in the site being currently scraped
        self.scrapped_data = {} # Emails found
        self.random_wait_time = '' # Time till the next query to google search
        self.total_result_pages_found = 1
        self.timeoutToFetchHtml = 5 # In seconds
        self.urls_with_errors = []
        self.result_pages_checked = result_pages_checked
        self.gtld =[] # Will contain all of the generic top level domains

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

        # Generic top level domains
        with open('gtld.csv', 'r') as fields:
            self.gtld = fields.read().split('\n')

    def parse_results(self):
        soup = self.BeautifulSoup(self.data.read(),"html5lib")
        for a in soup.select('.r a'):
            url = (a['href']).encode('ascii', 'ignore')
            self.links.append(url)

    def fetch_results(self):
        # Starts by fetching the current page obtained when initializing
        self.parse_results()

        # If more than one page of results is wanted
        if self.result_pages_checked > 1:

            for i in range(1, self.result_pages_checked):
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
            self.urls_with_errors.append(url)
            return False

    def find_email(self):
        pattern = self.re.compile(r'[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+')

        for x in self.re.findall(pattern, self.site_html.text):
            current_email_gtld = x.rsplit('.', 1)[1].upper()

            if current_email_gtld in self.gtld:
                x.encode('ascii', 'ignore')
                self.emails_found.append(x)

        # Removes duplicates 
        list(set(self.emails_found))

    def random_number(self):
        number = self.sr.choice(xrange(self.minimum_time_per_page, self.maximum_time_per_page))
        self.random_wait_time = number

    def scrap_emails(self):
        self.fetch_results()
        finds = {}
        counter = 0

        for url in self.links:
            self.site_html = ''
            self.emails_found = []
            if self.fetch_html(url) is True:
                self.find_email()

                if is self.emails_found:
                    finds[counter] = {}
                    finds[counter]['url'] = url
                    finds[counter]['emails'] = self.emails_found

                    counter += 1

        self.scrapped_data['result_pages'] = {}
        self.scrapped_data['result_pages']['desired'] = self.result_pages_checked
        self.scrapped_data['result_pages']['found'] = self.total_result_pages_found
        self.scrapped_data['errors'] = self.urls_with_errors
        self.scrapped_data['finds'] = {}
        self.scrapped_data['finds'] = finds

        return self.scrapped_data

@app.route('/pages/<int:result_pages_checked>/search/<search_term>')
def search_in_google(result_pages_checked, search_term):
    crawl_it = Crawler(user_agent, search_term, minimum_time_per_page, maximum_time_per_page, result_pages_checked)
    return jsonify(crawl_it.scrap_emails()), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
