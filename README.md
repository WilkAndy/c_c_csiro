# Connecting and Collaborating in CSIRO

A ChatGPT-style app for finding and promoting connections and collaborations across CSIRO.

## Scraping data

`scrape.py` scrapes data from Google Scholar using the `scholarly` python package.  This requires repeatedly querying Google Scholar, which runs the risk of being banned by Google Scholar.  Hopefully you can just use the data I've scraped (which is in the `scraped_data` directory) and you won't need to run `scrape.py`.

## Preprocessing scraped data

`preprocess.py`

