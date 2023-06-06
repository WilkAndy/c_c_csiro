################################################################
# Preprocess the scraped data into something that may be useful
################################################################
import sys
import os
import json
import glob
from pathlib import Path

verbose = True

# make the directory for the output if it doesn't exist
try:
   os.makedirs("training_data")
except FileExistsError:
   pass

################################################################
# Get author IDs and names
author_file = os.path.join("scraped_data", "authors.txt")
if verbose: sys.stdout.write("Reading authors from " + author_file + "\n")
with open(author_file, "r") as f:
    author_list = json.load(f)
author_names_set = set([a["name"] for a in author_list])
author_names_ids = [(a["name"], a["scholar_id"]) for a in author_list]

################################################################
# Concatenate publications into something that may be useful
for author_name, author_id in author_names_ids:
    if verbose: sys.stdout.write("Author " + author_name + "\n")
    fns = glob.glob(os.path.join("scraped_data", author_id) + "_*.txt")
    out_str = ''
    for fn in fns:
        with open(fn, "r") as f:
            pub = json.load(f)
        if "bib" not in pub:
            continue
        try:
            title = pub["bib"]["title"]
            authors = pub["bib"]["author"].split("and")
            csiro_authors = [author_name] + list(author_names_set.intersection(set(authors)))
        except:
            title = ""
            csiro_authors = [author_name]
        try:
            abstract = pub["bib"]["abstract"]
        except:
            abstract = ""
        csiro_authors = list(set(csiro_authors))
        csiro_authors = " and ".join(csiro_authors)
        abstract = " ".join(abstract.split())
        out_str += "Title: " + title + "\n"
        out_str += "CSIRO authors: " + csiro_authors + "\n"
        out_str += abstract + "\n"
    if len(out_str) > 0:
        out_fn = os.path.join("training_data", author_id + ".txt")
        with open(out_fn, "w") as f:
            f.write(out_str)
sys.exit(0)
