import urllib.request as req
from html.parser import HTMLParser
import pandas as pd


class myhtmlparser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.data = []

    def handle_data(self, _data):
        _data.replace('\\xa0', '')

        self.data.append(_data)

    def clean(self):
        self.data = []


"""
    Scrape the Irish Chess Union ratings website for my rating using icu id
    Parse the HTML
    Find the index for my name
    Add it to the output list
"""
with req.urlopen('https://ratings.icu.ie/icu_ratings?icu_id=18250') as response:
    html = response.read()
    parser = myhtmlparser()
    parser.feed(str(html))

# Extract data from parser
data = parser.data
ind = data.index('Fitzpatrick, Daniel')
output = [['Irish Chess Union', data[ind + 2], data[ind + 4]]]

"""
    Scrape the FIDE ratings website for my ratings using fide id
    Parse the HTML
    Find the index for std. (classical) rating
    Find the index for rapid rating
    find the index for blitz rating
"""
with req.urlopen('https://ratings.fide.com/card.phtml?event=2512513') as response:
    html = response.read()
    parser = myhtmlparser()
    parser.feed(str(html))

data = parser.data
ind = data.index('std.')
output.append(['FIDE Classical', '', data[ind + 1].replace('\\n', '')])

ind = data.index('rapid')
output.append(['FIDE Rapid', '', data[ind + 1].replace('\\n', '')])

ind = data.index('blitz')
output.append(['FIDE blitz', '', data[ind + 1].replace('\\n', '')])

pd.DataFrame(output).to_csv("ratings.csv", index=False, header=False)
