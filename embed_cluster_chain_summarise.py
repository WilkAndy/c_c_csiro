################################################################
# Summarise the publications of each author in scraped_data
# The abstracts of each author are grouped into a small number
# of topics depending on their semantic similarity (defined
# through OpenAIEmbeddings).  Then the abstracts in each topic
# are summarised using OpenAI, and finally these summaries
# are also summarised into an overall short paragraph.
#
# This code is somewhat based on Isaac Tham's work described at
# https://towardsdatascience.com/summarize-podcast-transcripts-and-long-texts-better-with-nlp-and-ai-e04c89d3b2cb
# and https://github.com/thamsuppp/llm_summary_medium
################################################################
import sys
import os
import json
import glob
from langchain.prompts import PromptTemplate
from langchain import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
import numpy as np
from scipy.spatial.distance import cosine
from networkx.algorithms import community
import networkx as nx

if "OPENAI_API_KEY" not in os.environ:
   os.environ["OPENAI_API_KEY"] = 'copy_and_paste_your_openai_api_key_here'
if os.environ["OPENAI_API_KEY"] == 'copy_and_paste_your_openai_api_key_here':
   sys.stderr.write("**************************************************\n")
   sys.stderr.write("*  This script needs a valid OPENAI_API_KEY      *\n")
   sys.stderr.write("*  See                                           *\n")
   sys.stderr.write("*  https://platform.openai.com/account/api-keys  *\n")
   sys.stderr.write("**************************************************\n")
   sys.exit(1)

verbose = True
# make the directory for some output if it doesn't exist
try:
   os.makedirs("embeddings")
except FileExistsError:
   pass
try:
   os.makedirs("scientific_themes")
except FileExistsError:
   pass

def get_themes(abstracts: list, verbose: bool) -> str:
   '''Return the themes (as a string) according to OpenAI, in the abstracts,
   which is a list of strings
   '''
   docs = [Document(page_content = a) for a in abstracts] 
   docs_num_tokens = sum([len(a.split()) for a in abstracts]) # total number of tokens in docs

   print(docs_num_tokens)
      
   #openai.error.InvalidRequestError: This model's maximum context length is 4097 tokens, however you requested 4233 tokens (3977 in your prompt; 256 for the completion). Please reduce your prompt; or completion length.
   if OpenAI(model_name = 'text-davinci-003').modelname_to_contextsize('text-davinci-003') > docs_num_tokens + 400:
      # can fit all the docs, prompts, output into the context window
      if verbose: sys.stdout.write("    Summarising " + str(len(abstracts)) + " titles+abstracts using chain_type = stuff\n")
      llm = OpenAI(temperature=0, model_name = 'text-davinci-003')
      prompt_template = """In 100-200 words, describe the scientific themes in the following text:
      {text}
      
      SCIENTIFIC THEMES:"""
      prompt = PromptTemplate(template = prompt_template, input_variables = ["text"])
      chain = load_summarize_chain(chain_type = "stuff", prompt = prompt, llm = llm)
      result = chain.run(docs)
   else:
      # too many docs to fit into context window, so use map_reduce
      if verbose: sys.stdout.write("    Summarising " + str(len(abstracts)) + " titles+abstracts using chain_type = map_reduce\n")
      map_llm = OpenAI(temperature=0, model_name = 'text-davinci-003')
      reduce_llm = OpenAI(temperature=0, model_name = 'text-davinci-003', max_tokens = -1)
      map_prompt_template = """Write a 50-100 word summary of the following text, focussing on the scientific themes:
      {text}
      
      SUMMARY:"""
      combine_prompt_template = """In 100-200 words, describe the scientific themes in the following text:
      {text}
      
      SCIENTIFIC THEMES:"""
      map_prompt = PromptTemplate(template = map_prompt_template, input_variables = ["text"])
      combine_prompt = PromptTemplate(template = combine_prompt_template, input_variables = ["text"])
      chain = load_summarize_chain(chain_type="map_reduce", map_prompt = map_prompt, combine_prompt = combine_prompt, return_intermediate_steps = False, llm = map_llm, reduce_llm = reduce_llm)
      result = chain({"input_documents": docs}, return_only_outputs = True)["output_text"]
   return result.strip()
   

################################################################
# Get author IDs and names
author_file = os.path.join("scraped_data", "authors.txt")
if verbose: sys.stdout.write("Reading authors from " + author_file + "\n")
with open(author_file, "r") as f:
    author_list = json.load(f)
author_names_set = set([a["name"] for a in author_list])
author_names_ids = [(a["name"], a["scholar_id"]) for a in author_list]

for author_name, author_id in author_names_ids[:3]: # TODO
   ################################################################
   # Get publications of each author
   if verbose: sys.stdout.write("Author " + author_name + "\n")
   out_fn = os.path.join("scientific_themes", author_id + ".txt")
   if os.path.exists(out_fn):
      continue

   if verbose: sys.stdout.write("  Extracting titles and abstracts\n")
   fns = glob.glob(os.path.join("scraped_data", author_id) + "_*.txt")
   titles_and_abstracts = []
   for fn in fns:
      with open(fn, "r") as f:
         pub = json.load(f)
      if "bib" not in pub:
         continue
      try:
         title = pub["bib"]["title"]
         authors = pub["bib"]["author"].split("and")
         csiro_authors = [author_name] + list(author_names_set.intersection(set(authors)))
         abstract = pub["bib"]["abstract"]
         csiro_authors = list(set(csiro_authors))
         csiro_authors = " and ".join(csiro_authors)
         abstract = " ".join(abstract.split())
      except:
         continue
      titles_and_abstracts.append(title + ". " + abstract)

   ################################################################
   # Find similarities of the titles+abstracts using Embeddings
   # and the cosine similarity between the embeddings for each
   # title+abstract
   fn = os.path.join("embeddings", author_id + "_embeddings.npy")
   if os.path.exists(fn):
      if verbose: sys.stdout.write("  Loading embeddings\n")
      abstract_embeds = np.load(fn)
   else:
      if verbose: sys.stdout.write("  Creating embeddings\n")
      openai_embed = OpenAIEmbeddings()
      abstract_embeds = np.array(openai_embed.embed_documents(titles_and_abstracts))
      np.save(fn, abstract_embeds)
   num_abstracts = len(titles_and_abstracts)
   if num_abstracts != len(abstract_embeds):
      sys.stderr.write("The length of embeddings doesn't match the number of abstracts\n")
      sys.stderr.write("You should remove " + fn + " and re-run this script to regenerate the embeddings\n")
      sys.exit(1)
      
   if verbose: sys.stdout.write("  Calculating similarity matrix\n")
   abstract_similarity_matrix = np.zeros((num_abstracts, num_abstracts))
   abstract_similarity_matrix[:] = np.nan
   for row in range(num_abstracts):
      for col in range(row, num_abstracts):
         # Calculate cosine similarity between the two vectors
         similarity = 1 - cosine(abstract_embeds[row], abstract_embeds[col])
         abstract_similarity_matrix[row, col] = similarity
         abstract_similarity_matrix[col, row] = similarity
   if False:
      import matplotlib.pyplot as plt
      plt.figure()
      plt.imshow(abstract_similarity_matrix, cmap = 'Blues')
      plt.show()
      plt.close()

   ################################################################
   # Using the similarities, cluster into a small number of topics.
   # Assume that authors with <= 8 papers probably publish on just 1 topic
   # Assume that the number of topics an author publishes on is num_abstracts / 8
   # Assume that an author never publishes on more than 6 topics
   num_topics = min([int(float(num_abstracts) / 8 + 0.5), 6])
   if verbose: sys.stdout.write("  Clustering the " + str(num_abstracts) + " abstracts into " + str(num_topics) + " topics\n")
   graph = nx.from_numpy_array(abstract_similarity_matrix)
   resolution = 0.0 # resolution = 0 means all the abstracts are clustered into 1 topic
   resolution_step = 0.01
   clusters = []
   potential_clusters = [[]] # those where the abstracts have been clustered into num_topics topics
   while resolution < 100 and len(clusters) <= num_topics:
      clusters = community.louvain_communities(graph, weight = 'weight', resolution = resolution)
      if len(clusters) == num_topics: # a desired clustering has been found
         potential_clusters.append(clusters)
      resolution += resolution_step # as resolution increases, the abstracts get clustered into more topics
   if len(potential_clusters) == 1: # louvain_communities must have failed
      potential_clusters.append(clusters)
   potential_clusters.pop(0) # remove the []
   # Assume the best clustering is one that has a similar number of abstracts in each topic
   cluster_sizes = [[len(topic) for topic in pc] for pc in potential_clusters]
   cluster_std = [np.std(cs) for cs in cluster_sizes]
   most_uniform_clustering = cluster_std.index(min(cluster_std))
   clusters = potential_clusters[most_uniform_clustering]

   ################################################################
   # Find the scientific theme(s) in each cluster
   if verbose: sys.stdout.write("  Finding the scientific theme(s) in each topic\n")
   summaries = [] # summaries[i] = summary of the i_th topic
   for cluster in clusters: # run through the topics, summarising each one
      abstracts_for_this_topic = [titles_and_abstracts[i] for i in cluster]
      result = get_themes(abstracts_for_this_topic, True)
      summaries.append(result)

   ################################################################
   # Find the scientific themes for the entire body of work of this author
   if verbose: sys.stdout.write("  Summarising the scientific themes in the abstracts of " + author_name + "\n")
   print(summaries)
   overall = get_themes(summaries, False)

   ################################################################
   # Output
   out = {"Author name": author_name,
          "Author ID": author_id,
          "Number of abstracts retrieved": num_abstracts,
          "Overall themes": overall,
          "Number of topics": len(clusters),
          "Number of abstracts in topics": [len(c) for c in clusters],
          "Themes in each topic": summaries}
   with open(out_fn, "w") as f:
      json.dump(out, f)

sys.exit(0)
