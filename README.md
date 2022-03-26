# 6998 Project 2

## Author:

- Ruobing Wang - rw2904
- Shunqiao Huang - sh4153


## Files:

- main.py
- example_relations.py
- spacy_help_functions.py
- SpanBERT


## Instructions

- install dependencies
	- python-3
	- beatiful soup
		- pip3 install beautifulsoup4
	- spaCy
		- pip3 install -U pip setuptools wheel
		- pip3 install -U spacy
		- python3 -m spacy download en_core_web_lg
	- googleapiclient-2.37.0
		- pip install google-api-python-client
- run command
	- **python3 main.py \<google api key> \<google engine id> \<relation> \<threshold> \<query> \<top k>**


## Design 

- Overview
	- We implemented a Iterative Set Expansion system that accepts query as input and expands the query based on the semantic meaning and entity relationship. 

- external library
	- beautiful soup
		- extract plain text from webpage
	- spaCy
		- extract name entities from plain text with tag
	- SpanBERT 
		- predict relationship based on extracted entities and tag


## Step 3

- Given URL, we use external library beautiful soup to obtain the plain text, limited to 2000 characters
- Given plain text, we use external library spaCy to extract the name entities
- Given name entites and entities of interest, generate the entity pairs
- Given entities pairs, we filter them based on whether the subject and object can form the desired relation
- Given filtered entities pairs, use external library SpanBERT to predict the relationship of the entity pair
- Consider the result pair if (1)the two entities have the relation that we are looking for, (2)these pair never exist previously or it has a higher confidence score than last time appeared, (3)the confidence score of the predicted relation between two entities passes the given threshold


## IDs

- Google Custom Search Engine JSON API Key
	- **AIzaSyCGx6yVlL5-grgZwMW4j6z3Ypf6YYq9_nY**
- Engine ID
	- **09cdf06c9bbdfd2dc**






