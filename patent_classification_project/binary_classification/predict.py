import pickle
from .function.webscraper_USPTO import *
from .function.pre_process_and_metrics import *
from .function.webscraper_EPO import *


model = pickle.load(open("binary_classification/PICKLE/model_binary_claims.pickle", "rb"))
tfidf_vect = pickle.load(open("binary_classification/PICKLE/tfidf_binary_claims.pickle", "rb"))


def predict(pub_num):
    
    pub_num = pub_num.upper().replace(' ', '')

    auth = pub_num[:2]


    if auth == 'US':
        #USPTO patent
        pat_num = pub_num[2:]

        #scrapes claims from a patent
        title, fam_id, claims, num_claims, db, url = web_scrap(pat_num)
        
        #this is when the patent does not exist
        if db.shape[0] == 0:
            result = {'Patent not found. Please try with a different publication number - see notes in the Input values box above': ''}
            dictionary = {'No claims found': ''}
            url = ""
            
            return result, dictionary, url

        # pre-process the claims
        db = pre_process_db(db)

        #check if the claims are split well
        num = ['1','2','3', '4', '5', '6', '7', '8', '9', '0']
        for i in db['Text']:
            if i[0:1] in num:

                result = {'Web scraping halted because the claims could not be split correctly': pub_num}
                dictionary = ""
                
                return result,dictionary, url
        
        #if the patent exists and the claims are correctly split
        #transforms the words in vectors using TFIDF
        X_tf = tfidf_vect.transform(db['text_clean']).toarray()
        #add an extra column with the prediction of the claims  - where 0 labelled a process and 1 a product claim
        db['predicted_label'] = model.predict(X_tf)
        #calculates how much in percentage a patent is a product patent
        perc_product = calculate_perc_product_pat(db)


        db['predicted_label'] = db.predicted_label.replace(to_replace=[1,0], value=['PRODUCT CLAIM', 'PROCESS CLAIM'])#convert numeric label in strings
        result = {'Percentage of product patent' : perc_product, 'Title Patent' : title, 'Number of claims' : num_claims, 'Publication Number' : pub_num , 'Family ID' : fam_id  }
        
        #this creates a dictionary for the claims and their predicted labels
        db['Type_Text'] = db['Type'] + ':     ' + db['Text']
        dictionary = dict(zip(db['Type_Text'],  db['predicted_label']))
        #no need of the url so it will be deleted
        url = ""

    elif auth == 'EP':
        #EPO patent
        publn_nr = pub_num[-2:]
        pat_num =pub_num[2:-2]
        
        #to handle a Http404 response
        try:
            
            title, fam_id, claims, num_claims, db = web_scrape_EPO(pat_num,publn_nr)
            # pre-process the claims
            db = pre_process_db(db)
            #transform in words in vectors using TFIDF
            X_tf = tfidf_vect.transform(db['text_clean']).toarray()
            db['predicted_label'] = model.predict(X_tf)
            perc_product = calculate_perc_product_pat(db)

            db['predicted_label'] = db.predicted_label.replace(to_replace=[1,0], value=['PRODUCT CLAIM', 'PROCESS CLAIM'])
            result = {'Percentage of product patent' : perc_product, 'Title Patent' : title, 'Number of claims' : num_claims, 'Publication Number' : pub_num , 'Family ID' : fam_id  }
            db['Type_Text'] = db['Type'] + ':     ' + db['Text']
            dictionary = dict(zip(db['Type_Text'],  db['predicted_label']))
            url = ""

        except:
            #trick to avoid opening a 404 page
            result = {'Patent not found. Please try with a different publication number - see notes in the Input values box above':''}
            dictionary = {'No claims found': ''}
            url = ""

    else:
        result = {'Patent not found. Please try with a different publication number - see notes in the Input values box above': ''}
        dictionary = {'No claims found': ''}
        url = ""

    return result, dictionary, url
