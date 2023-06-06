import sys
import os
import json
import arrow # so a ParserError can be handled below
try:
    from scholarly import scholarly
    from scholarly import ProxyGenerator
except:
    raise Exception("\n\n  You probably need to install scholarly via\n  pip3 install scholarly\n  Read the docs at: https://scholarly.readthedocs.io/en/stable/quickstart.html\n\n")

verbose = True
organisation = "CSIRO"
use_proxy = True

# make the directory for the output if it doesn't exist
try:
   os.makedirs("scraped_data")
except FileExistsError:
   pass

################################################
# Proxy
if use_proxy:
    if verbose: sys.stdout.write("Generating proxy\n")
    pg = ProxyGenerator()
    success = pg.FreeProxies() # can use other proxies, which usually cost $$$: see https://scholarly.readthedocs.io/en/stable/quickstart.html
    scholarly.use_proxy(pg)

################################################
# Get organisation ID
org_file = os.path.join("scraped_data", "org.txt")
if os.path.exists(org_file):
    if verbose: sys.stdout.write("Reading organisation ID from " + org_file + "\n")
    with open(org_file, "r") as f:
        org_dict = json.load(f)
else:
    if verbose: sys.stdout.write("Finding organisation ID from Google Scholar\n")
    org_dict = scholarly.search_org(organisation)
    with open(org_file, "w") as f:
        json.dump(org_dict, f)
org_id = int(org_dict[0]['id'])

################################################
# Get author IDs
author_file = os.path.join("scraped_data", "authors.txt")
author_list = []
if os.path.exists(author_file):
    if verbose: sys.stdout.write("Reading authors from " + author_file + "\n")
    with open(author_file, "r") as f:
        author_list = json.load(f)
else:
    if verbose: sys.stdout.write("Finding authors from Google Scholar\n")
    authors = scholarly.search_author_by_organization(org_id)
    author_list = [a for a in authors]
    with open(author_file, "w") as f:
        json.dump(author_list, f)

################################################
# Get publications
pub_titles = []
for a in author_list: # could shorten
    fn = os.path.join("scraped_data", a["scholar_id"] + ".txt")
    if os.path.exists(fn):
        if verbose: sys.stdout.write("Found all publications for author " + a["name"] + "\n")
        with open(fn, "r") as f:
            author_data = json.load(f)
    else:
        if verbose: sys.stdout.write("Finding all the publications for author " + a["name"] + "\n")
        partial_author_data = scholarly.search_author_id(a["scholar_id"])
        author_data = scholarly.fill(partial_author_data)
        with open(fn, "w") as f:
            json.dump(author_data, f)

    num = 0
    for pub in author_data['publications']: # could shorten
        num += 1
        fn = os.path.join("scraped_data", a["scholar_id"] + "_" + str(num) + ".txt")
        pub_title = pub["bib"]["title"]
        if pub_title not in pub_titles:
            pub_titles.append(pub_title)
            if verbose: sys.stdout.write("  " + str(num) + "/" + str(len(author_data['publications'])) + " " + pub_title + "\n")
            if not os.path.exists(fn):
                try:
                    article_info = scholarly.fill(pub)
                except arrow.parser.ParserError:
                    article_info = ' '
                with open(fn, "w") as f:
                    json.dump(article_info, f)
sys.exit(0)
