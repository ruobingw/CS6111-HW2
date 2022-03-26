import spacy
from spanbert import SpanBERT
from spacy_help_functions import get_entities, create_entity_pairs

# tuple_dict = ((Subject, Object): Confidence, ():...)
def process_plain_text(raw_text, r, t, tuple_dict): 
    
    '''
    raw_text = "Zuckerberg attended Harvard University, where he launched the Facebook social networking service from his dormitory room on February 4, 2004, with college roommates Eduardo Saverin, Andrew McCollum, Dustin Moskovitz, and Chris Hughes. Bill Gates stepped down as chairman of Microsoft in February 2014 and assumed a new post as technology adviser to support the newly appointed CEO Satya Nadella. "
    '''

    entities_of_interest = ["ORGANIZATION", "PERSON", "LOCATION", "CITY", "STATE_OR_PROVINCE", "COUNTRY"]

    # Load spacy model
    nlp = spacy.load("en_core_web_lg")  

    # Load pre-trained SpanBERT model
    spanbert = SpanBERT("./pretrained_spanbert")

    # Apply spacy model to raw text (to split to sentences, tokenize, extract entities etc.)
    doc = nlp(raw_text) 

    total_sen = 0
    for sentence in doc.sents: total_sen += 1
    print("Extracted " + str(total_sen) + " sentences. Processing each sentence one by one to check for presence of right pair of named entity types; if so, will run the second pipeline ...")

    result = {}
    extracted_sen = 0
    cur_result = []
    total_extracted = 0
    for i, sentence in enumerate(doc.sents): 
        ents = get_entities(sentence, entities_of_interest)
        
        # create entity pairs
        candidate_pairs = []
        sentence_entity_pairs = create_entity_pairs(sentence, entities_of_interest)
        for ep in sentence_entity_pairs:
            # keep subject-object pairs of the right type for the target relation (e.g., Person:Organization for the "Work_For" relation)
            if r == "per:employee_of" or r == "per:schools_attended":
                if ep[1][1] == "PERSON" and ep[2][1] == "ORGANIZATION":
                    candidate_pairs.append({"tokens": ep[0], "subj": ep[1], "obj": ep[2]})  # e1=Subject, e2=Object
                elif ep[1][1] == "ORGANIZATION" and ep[2][1] == "PERSON":
                    candidate_pairs.append({"tokens": ep[0], "subj": ep[2], "obj": ep[1]})  # e1=Object, e2=Subject
            elif r == "per:cities_of_residence":
                if ep[1][1] == "PERSON" and (ep[2][1] == "LOCATION" or ep[2][1] == "CITY" or ep[2][1] == "STATE_OR_PROVINCE" or ep[2][1] == "COUNTRY"):
                    candidate_pairs.append({"tokens": ep[0], "subj": ep[1], "obj": ep[2]})
                elif (ep[1][1] == "LOCATION" or ep[1][1] == "CITY" or ep[1][1] == "STATE_OR_PROVINCE" or ep[1][1] == "COUNTRY") and ep[2][1] == "PERSON":
                    candidate_pairs.append({"tokens": ep[0], "subj": ep[2], "obj": ep[1]})
            elif r == "org:top_members/employees":
                if ep[1][1] == "PERSON" and ep[2][1] == "ORGANIZATION":
                    candidate_pairs.append({"tokens": ep[0], "subj": ep[2], "obj": ep[1]})  
                elif ep[1][1] == "ORGANIZATION" and ep[2][1] == "PERSON":
                    candidate_pairs.append({"tokens": ep[0], "subj": ep[1], "obj": ep[2]}) 

        # Classify Relations for all Candidate Entity Pairs using SpanBERT
        candidate_pairs = [p for p in candidate_pairs if not p["subj"][1] in ["DATE", "LOCATION"]]  # ignore subject entities with date/location type
        
        if len(candidate_pairs) == 0:
            if i != 0 and i%5 == 0:
              print("Processed " + str(i) + " / " + str(total_sen) + " sentences")
            continue
        
        relation_preds = spanbert.predict(candidate_pairs)  # get predictions: list of (relation, confidence) pairs
        
        cur_result += list(zip(candidate_pairs, relation_preds))       
        if i != 0 and i%5 == 0:
          print("Processed " + str(i) + " / " + str(total_sen) + " sentences")
          for ex, pred in cur_result:
            # reached number of tuples that we request in the output
            # reached minimum extraction confidence that we request for the tuples in the output
            if pred[0] == r:
              total_extracted += 1
              print("\n=== Extracted Relation ===")
              print("Input tokens: ", ex["tokens"])
              print("Output Confidence: {:.2f} ; Subject: {} ; Object: {} ;".format(pred[1], ex["subj"][0], ex["obj"][0]))
              if pred[1] >= t:
                cur_tuple_key = (ex["subj"][0], ex["obj"][0])
                cur_tuple_value = pred[1]
                if cur_tuple_key in tuple_dict:
                  if tuple_dict[cur_tuple_key] < cur_tuple_value:
                    print("Adding to set of extracted relations")
                    result[cur_tuple_key] = cur_tuple_value
                  else:
                    print("Duplicate with lower confidence than existing record. Ignoring this.")
                elif cur_tuple_key in result:
                  if result[cur_tuple_key] < cur_tuple_value:
                    print("Adding to set of extracted relations")
                    result[cur_tuple_key] = cur_tuple_value
                  else:
                    print("Duplicate with lower confidence than existing record. Ignoring this.")
                else:
                  print("Adding to set of extracted relations")
                  result[cur_tuple_key] = cur_tuple_value
                extracted_sen += 1
              else:
                print("Duplicate with lower confidence than existing record. Ignoring this.")
              print("==========")

          cur_result = []

    return result, total_extracted, extracted_sen, total_sen

            
