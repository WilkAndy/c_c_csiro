####################################################################
# Load documents into a VectorStoreIndex, and then query it
####################################################################

import os
import sys
import glob
from llama_index import VectorStoreIndex, SimpleDirectoryReader, ListIndex

if "OPENAI_API_KEY" not in os.environ:
   os.environ["OPENAI_API_KEY"] = 'copy_and_paste_your_openai_api_key_here'
if os.environ["OPENAI_API_KEY"] == 'copy_and_paste_your_openai_api_key_here':
   sys.stderr.write("**************************************************\n")
   sys.stderr.write("*  This script needs a valid OPENAI_API_KEY      *\n")
   sys.stderr.write("*  See                                           *\n")
   sys.stderr.write("*  https://platform.openai.com/account/api-keys  *\n")
   sys.stderr.write("**************************************************\n")
   sys.exit(1)

####################################################################
# Get Pep Canadell's titles + abstracts
# Pep Canadell has GoogleScholar ID 4QU11c4AAAAJ
version = 1
if version == 1:
    # scrape.py organised all his titles+abstracts into files named 4QU11c4AAAAJ_*.txt
    documents = SimpleDirectoryReader(input_files = glob.glob(os.path.join("scraped_data", "4QU11c4AAAAJ_*.txt"))).load_data()
elif version == 2:
    # preprocess.py has organised them all into 4QU11c4AAAAJ.txt
    documents = SimpleDirectoryReader(input_files = glob.glob(os.path.join("training_data", "4QU11c4AAAAJ.txt"))).load_data()
else:
    sys.stderr.write("Version number " + str(version) + " not yet coded!\n")
    sys.exit(1)

####################################################################
# load info into VectorStoreIndex and query
index = VectorStoreIndex.from_documents(documents)
#index = ListIndex.from_documents(documents) # this is an alternate
query_engine = index.as_query_engine()
query = input("Ask something about Pep Canadell.., for instance: In 100-200 words, what are the scientific themes that Pep Canadell from CSIRO has published on? ")
response = query_engine.query(query)
print(response)

sys.exit(0)
