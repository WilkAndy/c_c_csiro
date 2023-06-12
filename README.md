# LLMs and chatGPT: lessons learned in June 2023

Most scientific authors publish on a small handful of themes.  Suppose we want to find those themes by analysing the abstracts of the author's publications.  This page summarises various ways, along with some pros and cons, of achieving this.  I'm going to use Pep Canadell from CSIRO as my test subject, because he is highly cited.  Using [scrape.py](scrape.py), 403 titles and abstracts written by Pep were retrieved from Google Scholar.

## Use ChatGPT

Pros/Cons:

- Requires no coding
- Not able to include appreciable new data (a small amount of data may be included in the prompt).  ChatGPT does not include post-2021 data
- Works for popular authors such as Pep, but ChatGPT does not know about less popular authors
- For these authors, Appears to give reasonable results
- Comes at a small financial cost (unless you're still in your free-trial period).

> My prompt: "In 100-200 words, what are the scientific themes that Pep Canadell from CSIRO has published on?"

> ChatGPT's completion: "Dr. Pep Canadell is a renowned scientist who has made significant contributions to the field of global carbon cycle science. He has conducted extensive research on topics related to carbon dioxide emissions, atmospheric greenhouse gases, climate change, and the carbon cycle. As the Executive Director of the Global Carbon Project and a researcher at the CSIRO (Commonwealth Scientific and Industrial Research Organisation), Dr. Canadell has published on various scientific themes.

> "Some of the key scientific themes that Dr. Pep Canadell has published on include:

> "   Carbon Budgets and Accounting: He has focused on estimating and quantifying global and regional carbon budgets, which involves understanding the sources and sinks of carbon dioxide and other greenhouse gases.

> "   Land Use and Ecosystems: Dr. Canadell has investigated the role of land use changes, such as deforestation and afforestation, on the carbon cycle and its implications for climate change mitigation.

> "   Climate Change Mitigation: He has contributed to studies on the effectiveness of different mitigation strategies, including the evaluation of emission reduction targets, carbon pricing mechanisms, and the potential of carbon capture and storage.

> "   Climate Science and Policy: Dr. Canadell has provided scientific input to policy discussions and international agreements on climate change, including the assessment reports of the Intergovernmental Panel on Climate Change (IPCC).

> "Dr. Pep Canadell's research and publications have helped advance our understanding of the global carbon cycle and its interactions with climate change. His work has been influential in shaping climate change mitigation strategies and informing climate policies at national and international levels."

## Use [CustomGPT](https://app.customgpt.ai/)

Pros/Cons:

- Able to train on any data supplied (for the example below, the file `training_data/4QU11c4AAAAJ.txt` was used)
- Appears to give reasonable results
- Some coding may be required for creating the training data, but CustomGPT itself just requires upload of the data
- Costs USD50/month

> My prompt: "In 100-200 words, what are the scientific themes that Pep Canadell from CSIRO has published on?"

> CustomGPT's completion: "Pep Canadell from CSIRO has published on various scientific themes related to the carbon cycle, climate change, and ecosystems. Some of the key topics include:

> " 1. Processes affecting terrestrial carbon stocks and human influences upon them.
> " 2. Emerging trends in carbon cycle science, focusing on the behavior of the carbon cycle under continuous warming and low emissions scenarios, carbon-climate feedbacks, and responses to climate extremes.
> " 3. The role of plants in absorbing CO2 and its implications.
> " 4. A global research agenda on the carbon-climate-human system, including routine updates of global and regional carbon budgets, assessment of the carbon-climate feedback magnitude, and exploration of pathways to climate stabilization.
> " 5. Combating ecosystem collapse and its impact on biodiversity, human health, and well-being.
> " 6. Interdisciplinary joint projects on carbon, food, water, and health, and their role in advancing integrated Earth system knowledge.
> " 7. The global carbon cycle as a test of our knowledge of Earth as a system, focusing on the role of individual components in the global carbon cycle due to human activities since the Industrial Revolution.

## Embed, cluster, chain-summarize using LangChain and OpenAI

The code is described in full in [embed_cluster_chain_summarise.py](embed_cluster_chain_summarise.py).  In short, the abstracts are embedded (using `OpenAIEmbeddings`), clustered into a small number of topics (using `networkx.algorithms.community.louvain_communities`), then each topic is summarised (using `langchain.chains.summarize` and an OpenAI `text-davinci-003`) and a final summary is produced.

Pros/Cons:

- Customisable
- Coding required
- Appears to give reasonable results
- Costs about USD4 to embed and summarise Pep's 403 abstracts

Output:

> "Overall themes": "Global Carbon Cycle, Carbon-Climate Feedback, Responses to Climate Extremes, Effects of Global Warming on Carbon Cycle, Effects of Rising CO2 Concentrations, Interactions between Carbon Cycle, Human Activity, and Climate System, Effects of Land Use Change on Carbon Cycle, Human Perturbation of Carbon Cycle, Vulnerability of Permafrost Carbon to Climate Change, Potential Feedbacks from Terrestrial Ecosystems to Atmosphere, Rate and Form of Release of Carbon, Impact of Climate Extremes on Terrestrial Carbon Cycle, Role of Peatlands in Global Carbon Cycle, Potential Future Impacts of Climate Change on Carbon Cycle, Nitrogen Budget, Methane Emissions, Nitrous Oxide Emissions, Global Methane Budget, Methane Removal, Methane Hydrates, Fluxnet, Nitrous Oxide Budget, Tree Exchange of Nitrous Oxide, Top-Down and Bottom-Up Approaches to Nitrous Oxide Budget, Biogeochemical Cycles of Carbon Dioxide, Methane and Nitrous Oxide, Nitrous Oxide Mitigation Potential, Greenhouse Gases, Hydroxyl Radicals, Atmospheric Inversions, El Nino Events, Process-Based Models, Inventories, Data-Driven Approaches, Observational"






## Getting started

I'm using python 3.10.  Probably later versions work fine.  The required python packages may be installed using:

`pip install -r requirements.txt`

# Connecting and Collaborating in CSIRO

The original purpose of this repository was to explore how LLMs could help with connecting and collaborating across CSIRO.  I had hoped a LLM could answer questions such as "What models has CSIRO created in the field of fisheries?" and "What sort of models and/or data could be coupled with these fisheries models to add value to CSIRO research?" and "Who are some people who'd be suited to creating this systems model?".  I hoped to train the LLM on titles and abstracts of CSIRO work.  This turned out to be too ambitious, but I learned stuff along the way and wanted to document it here.

## Scraping data

`scrape.py` scrapes data from Google Scholar using the `scholarly` python package.  This requires repeatedly querying Google Scholar, which runs the risk of being banned by Google Scholar.  Hopefully you can just use the data I've scraped (which is in the `scraped_data` directory) and you won't need to run `scrape.py`.
