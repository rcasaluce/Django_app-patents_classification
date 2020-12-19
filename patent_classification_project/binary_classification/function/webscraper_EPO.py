#!/usr/bin/env python
# coding: utf-8
# %%
import urllib.request

import pandas as pd
from bs4 import BeautifulSoup
import time
import requests

# %%
import epo_ops
import re

def web_scrape_EPO(pat_num, publn_kind):
    
	#set client for 
	# Retrieve claims data
	client = epo_ops.Client(key='', secret='')  # Instantiate client
	response = client.published_data(  
	reference_type = 'publication',
	input = epo_ops.models.Docdb(str(pat_num), 'EP', publn_kind),  
	endpoint = 'claims', 
	constituents = []  
	)
     # Retrieve bibliography data
	response2 = client.published_data( 
	reference_type = 'publication', 
	input = epo_ops.models.Docdb(str(pat_num), 'EP', publn_kind),
	endpoint = 'biblio', 
	constituents = []  
	)
	claims = response.text
	claims = re.split('\s+', claims)#split in a list of words
	start_eng_claims = ['lang="EN"']
	match_first_claim = [string for string in claims if any(xstring in string for xstring in start_eng_claims)]# match string that includes 'lang="EN"' 
	index = claims.index(match_first_claim[0])# to avoid the squared brackets
	eng_claims = claims[index:]
	eng_claims = ' '.join(eng_claims)
	list_claims = re.findall(r'<claim-text>[0-9]+\..*?</claim-text>', str(eng_claims))
	#for the title
	title = response2.text
	title_list = re.findall(r'<invention-title lang="en">(.*)</invention-title>', str(title))
	family_id = re.findall(r'family-id="([a-zA-Z]?[0-9]+)"', str(title))
    
	def split_claims(ls_claims):
	
		for items in range(len(ls_claims)):   
			ls_claims[items] = str(ls_claims[items]).replace("<claim-text>", "")
			ls_claims[items] = str(ls_claims[items]).replace("</claim-text>", "")
    
		return ls_claims

	claim_list = split_claims(list_claims)
    
	publication_num = [pat_num]
    
	dataset = build_dataset(claim_list, title_list, publication_num,family_id)
	
	claims = dict(zip(dataset.Type, dataset.Text))
    
	num_claims = len(claims)
	title = dataset['Title'].iloc[0]
    
	fam_id =  dataset['Family_ID'].iloc[0]
	
	
    
	return title, fam_id, claims, num_claims, dataset


# %%
def build_dataset(claim_list, title_list, publication_num, family_id):
    
    """built a database in which the abstract and
    each claim has a separate line
    
    @*arg = it allows to add more columns in the database"""
    
    
    #list of patents with abstract and claims text in separate rows
    list_pat = []
        
    temp = []
        
    #temporary rows to be added 
    temp_2 = []
        
    for j in range(len(claim_list)):
            
        #set a new rows for each claims in a patent 
        new_ls = [publication_num[0],family_id[0], title_list[0]]
        claim = claim_list[j]
            
        if j == 0:
            #clean the first claim
            claim = re.sub(r'(.*?[\:\.]\s*'+str(j+1)+'\.\s*) ',"",str(claim)).strip() 
            b = '[\']'
            claim = claim.replace(b, "")
            new_ls.extend(['Claim ' + str(j+1), str(claim[2:])])
            
        else:
            #clean all the rest of the claims
            claim=re.sub(r'('+ str(j+1)+'\.\s+)',"",str(claim)).strip()
            claim=re.sub(r'([\"\"])|(\\)|([\'\'])|(\[\]) ',"",str(claim)).strip()
            claim=re.sub(r'\'',"",str(claim)).strip()
            new_ls.extend(['Claim ' + str(j+1), str(claim)])
            
        temp_2.append(new_ls)
        
    temp.extend(temp_2)
        
    list_pat.extend(temp)
   
    
    return pd.DataFrame(list_pat, columns = ['Publn_Nr','Family_ID', 'Title', 'Type', 'Text'])

# %%
# pat_num = '0019090'
# publn_kind = 'B1'        
# db= web_scrape_EPO(pat_num, publn_kind)
# #db = build_dataset(claim_list, title_list, publication_num)

# %%
