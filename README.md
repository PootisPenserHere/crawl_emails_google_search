# Google search email crawler

#### This script will run a google search and iterate through the resulting pages, scrapping from each of them the emails and returning them in a json format.

## Setting up the enviroment
### Requires python 2.7

### Installing the dependencies
```sh
pip install -r requirements.txt
```

## Getting started
#### To begin modify the script on the "Configuration variables" sectionto meet the desired criteria where:

### user_agent
#### This will be the user agent that the mechanize browser will use to connect the to the google search engine

### search_term
#### The subject of the search, this could be a general topic or use more detailed parameters so that google will return more specific results

### result_pages_checked
#### The number of results pages from the google search that will be iterated, should the desired number be higher than the available pages it'll be truncated
