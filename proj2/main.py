from googleapiclient.discovery import build
import numpy as np
import collections
import sys
import urllib
from bs4 import BeautifulSoup
from example_relations import process_plain_text
from socket import timeout
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Google Custom Search Engine JSON API Key
# AIzaSyCGx6yVlL5-grgZwMW4j6z3Ypf6YYq9_nY
# Engine ID
# 09cdf06c9bbdfd2dc

r_dict = {
    '1':"per:schools_attended",
    '2':"per:employee_of",
    '3':"per:cities_of_residence",
    '4':"org:top_members/employees"
}

def searchAPI(query, client_key, engine_key):
    # Build a service object for interacting with the API.
    service = build("customsearch", "v1", developerKey=client_key)
    res = service.cse().list(q=query, cx=engine_key).execute()

    result = []
    if "items" not in res:
        return []
    for search_item in res["items"]:
        result.append(search_item["link"])
    return result

def search(client_key, engine_key, relation, threshold, query, num_of_tuples):
    # Parameters info
    print("Parameters:")
    print("{:<12} {:<3} {:<10}".format("Client key", "=", client_key))
    print("{:<12} {:<3} {:<10}".format("Engine key", "=", engine_key))
    print("{:<12} {:<3} {:<10}".format("Relation", "=", relation))
    print("{:<12} {:<3} {:<10}".format("Threshold", "=", str(threshold)))
    print("{:<12} {:<3} {:<10}".format("Query", "=", query))
    print("{:<12} {:<3} {:<10}".format("# of Tuples", "=", str(num_of_tuples)))
    print("Loading necessary libraries; This should take a minute or so ...):")
    
    iteration = 0
    url_set = set()
    query_set = set()
    tuple_dict = {}
 
    while True:
        print("=========== Iteration: "+str(iteration)+" - Query: "+query+" ===========")

        query_result = searchAPI(query, client_key, engine_key)

        # if no result is return, nothing else can be done
        if len(query_result) == 0:
            print("No results returned")
            break

        for i in range(len(query_result)):
            if query_result[i] in url_set:
                continue
            url_set.add(query_result[i])

            print("URL ( "+str(i+1)+" / 10): "+query_result[i])
            print("Fetching text from url ...")

            # retrieve web page given url, skip the url if error or timeout
            try:
              req = Request(query_result[i], headers={'User-Agent': 'Mozilla/5.0'})
              page = urlopen(req, timeout=20).read()
            except (HTTPError, URLError) as error:
              continue
            except timeout:
              continue
            
            soup = BeautifulSoup(page, 'html.parser')

            # kill all script and style elements
            for script in soup(["script", "style"]):
                script.extract()

            # get text, skip empty or short sentences
            text = ""
            for line in soup.get_text().splitlines():
              line = line.strip()
              if line != "" and len(line.split(" ")) > 3:
                text += line + ". "

            if len(text) > 20000:
                print("Trimming webpage content from "+str(len(text))+" to 20000 characters")
                text = text[:20000]
            
            print("Webpage length (num characters): "+str(len(text)))
            print("Annotating the webpage using spacy...")

            # call process_plain_text to extract tuples
            new_tuple, total_extracted, extracted_sen, total_sen = process_plain_text(text, relation, threshold, tuple_dict)
            tuple_dict.update(new_tuple)

            print("Extracted annotations for  "+str(extracted_sen)+"  out of total  "+str(total_sen)+"  sentences")
            print("Relations extracted from this website: "+str(len(new_tuple))+" (Overall: "+str(total_extracted)+")")
        
        # if we not yet find reuqired number of tuples, find the unseen tuple with highest confidence
        if len(tuple_dict) < num_of_tuples:
          sorted_tuple = dict(sorted(tuple_dict.items(), key=lambda item: item[1], reverse=True))
          for tu_key, _ in sorted_tuple.items():
            if tu_key not in query_set:
              query += " " + tu_key[0] + " " + tu_key[1]
              query_set.add(tu_key)
              break

        iteration += 1
        
        # Summary
        print("================== ALL RELATIONS for "+relation+" ( "+str(len(tuple_dict))+" ) =================")
        sorted_tuple = dict(sorted(tuple_dict.items(), key=lambda item: item[1], reverse=True))
        for tu_key, tu_value in sorted_tuple.items():
            print("Confidence: "+str(tu_value)+" 		| Subject: "+tu_key[0]+" 		| Object: "+tu_key[1])
    
        if len(tuple_dict) >= num_of_tuples:
          break
    
    print("Total # of iterations = "+str(iteration))

def main():
    if len(sys.argv) != 7:
        print("Invalid Format")
        print("Expect: python3 project2.py <google api key> <google engine id> <r> <t> <q> <k>")
        return 

    # paramaters
    client_key = sys.argv[1]
    engine_key = sys.argv[2]
    relation = r_dict[sys.argv[3]]
    threshold = float(sys.argv[4])
    query = sys.argv[5]
    num_of_tuples = int(sys.argv[6])

    if threshold < 0 or threshold > 1: 
        print("Invalid Precision")
        print("Expect: 0 <= Precision <= 1")
        return
    
    if not len(query):
        print("Invalid Query")
        print("Expect: query length > 0")
        return

    search(client_key, engine_key, relation, threshold, query, num_of_tuples)

    return 


if __name__ == '__main__':
    main()


