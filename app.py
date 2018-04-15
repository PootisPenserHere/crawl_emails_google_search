import mechanize
from bs4 import BeautifulSoup
import re
import json

# Initialize the browser
browser = mechanize.Browser()
browser.set_handle_robots(False)
browser.set_handle_equiv(False)
browser.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0')]
browser.open('http://www.google.com.mx/')

# Querying to google
browser.select_form(name='f')
browser.form['q'] = 'python'
data = browser.submit() # Search result

# Returned data
links = []

# Parsing the html
soup = BeautifulSoup(data.read(),"html5lib")
for a in soup.select('.r a'):
    links.append(a['href'])

print json.dumps(links)
