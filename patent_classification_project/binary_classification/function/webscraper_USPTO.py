import urllib.request
import re
import pandas as pd
from bs4 import BeautifulSoup
import time
import requests
from timeit import default_timer as timer



def web_scrap(pat_num):
    
	start = timer()

	claim_list, title_list, publication_num, application_num, application_num_orig,  =([]for i in range(5))

		
	pat_num = str(int(pat_num))
	url = 'http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=1&p=1&f=G&l=50&d=PTXT&S1='+pat_num+'.PN.&OS=pn/'+pat_num+'&RS=PN/'+pat_num+''
	headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}


	time.sleep(5)

	req = urllib.request.Request(url, headers = headers)
	resp = urllib.request.urlopen(req)
	respData = resp.read()

	#searches for all the information needed for a patent using findall
	tit = re.findall(r"<FONT size\=\"\+1\">(.*?)</FONT>",str(respData))#title of the patent
	claim = re.findall(r'<CENTER><b><i>Claims</b></i></CENTER> <HR> <BR><BR>(.*?)<HR>',str(respData))
	publn_nr = re.findall(r'<TITLE>United States Patent: ([0-9]+)</TITLE>',str(respData))#Title num of the patent
	fam_id = re.findall(r'Family ID.*?(\d{5,9}).*?Appl. No.', str(respData))#Family ID
	appl_num = re.findall(r'Appl. No.:.*?<b>(.*?)</b>', str(respData))#Appl. No. ex. 08/544,281
	appl_num_orig = re.findall(r'<U>Publication Date.*?(US\s+[0-9]+\s+[A-Z][0-9])', str(respData))#ex. 'US 20080246285 A1'
	soup = BeautifulSoup(respData,'html.parser')

	#append the string to each lists
	if len(publn_nr) == 0:
		publn_nrs = ''
	else:
		publn =  list(publn_nr)#convert the string found in a list of chracters
		publn_nrs = ''.join(publn)#join back in a string to get rid of the squared brackets
	publication_num.append(publn_nrs)

	if len(fam_id) == 0:
		fam_ids = 'NA'
	else:
		fam_ids =  fam_id
	family_id = fam_id
	#family_id.append(fam_ids)

	if len(appl_num) == 0:
		appl_nums = ''
	else:
		appl_nums =  re.sub(r'[[\' /, \]]',"",str(appl_num)).strip()#ex. from [' 08/544,281'] to ['08544281']
	application_num.append(appl_nums)

	if len(appl_num_orig) == 0:
		appl_num_origs = ''
	else:
		appl_num_or =  list(appl_num_orig)#see for publn_nr
		appl_num_origs = ''.join(appl_num_or)    
	application_num_orig.append(appl_num_origs)

	if len(claim)==0:
		claims = 'NA'
	else:
		claims = claim
	claim_list.append(claims)

	if len(tit)==0:
		titl = 'NA'
	else:
		titl = tit
	title_list.append(titl)


	#to clean the strings
	for items in range(len(title_list)):   
		title_list[items] = str(title_list[items]).replace("\\n", "")
		title_list[items] = str(title_list[items]).replace("\\", "")
		title_list[items] = title_list[items][1:-1] 
		claim_list[items] = re.sub(r'<BR>',"",str(claim_list[items])).strip() 
		claim_list[items] = claim_list[items].replace("\\n", "")
		claim_list[items] = claim_list[items].replace("\\", " ")
		claim_list[items] = claim_list[items][1:-1]
		
		
	claim_list = split_claims(claim_list)

	dataset = build_dataset(claim_list, title_list, publication_num, family_id, application_num, application_num_orig)

	end = timer()

	web_scrape_time = end - start

	print('web_scrap: {}'.format(web_scrape_time))

	claims = dict(zip(dataset.Type, dataset.Text))

	num_claims = len(claims)
	
	print(dataset.shape[0], 'dataset.shape[0]')
	print(dataset, 'dataset')
	if dataset.shape[0] != 0:
		title = dataset['Title'].iloc[0]
		fam_id =  dataset['Family_ID'].iloc[0]
	else:
		title = ''
		fam_id = ''


	return title, fam_id, claims, num_claims, dataset, url



def split_claims(ls_claim):
    
	"""splits the claims
	@ls_claim = list of claims"""

	claim_sep = []

	for j in range(len(ls_claim)):
		if ls_claim[j] != 'NA':
			claim = []
			claim_minus_1 = re.findall(r'\.(\s+2.*)',str(ls_claim[j]))#everything from claim 2
			claim_counter = re.findall(r'\.\s+([0-9]+)\.',str(ls_claim[j]))#numeric list from the second cl to the end
			claim_one = re.findall(r'(^.*?.)\s+2\. ',str(ls_claim[j]))#first claim
			
			claim.extend(claim_one)
			
			count = len(claim_counter)
			
			for i in range(len(claim_counter)):
				if count >= 2:
					if i ==0:
						regular =  '[\"\']\s*(2\.\s+.*?[a-zA-Z]+.*?)\s*3\.'#for the claim 2
						next_claim = re.findall(regular,str(claim_minus_1))
						claim.extend(next_claim)
					else:
						regular =  '\.\s*( '+ claim_counter[i]+'\.\s+.*?[a-zA-Z]+.*?)\s*'+claim_counter[i+1]+'\.'
						next_claim = re.findall(regular,str(claim_minus_1))
						claim.extend(next_claim)
				else:
					regular =  '.\s+('+claim_counter[i]+'\. .*?[a-zA-Z]+.*?.*)]'#for the last claim
					next_claim = re.findall(regular,str(claim_minus_1))
					claim.extend(next_claim)
				count -= 1       
		else:
			continue
		claim_sep.append(claim)


	return claim_sep


def build_dataset(claim_list, title_list, publication_num, family_id, application_num, application_num_orig):

	"""built a database in which the abstract and
	each claim has a separate line

	@*arg = it allows to add more columns in the database"""


	#list of patents with abstract and claims text in separate rows
	list_pat = []

	for i in range(len(claim_list)):
		
		
		
		#set the first row of the patents with only the text for the abstract
		
		temp = []
		
		#temporary rows to be added 
		temp_2 = []
		
		for j in range(len(claim_list[i])):
			
			#set a new rows for each claims in a patent 
			new_ls = [publication_num[i], family_id[i], application_num[i] , application_num_orig[i], title_list[i][1:-1]]
			claim = claim_list[i][j]
			
			if j == 0:
				#clean the first claim
				claim = re.sub(r'(.*?[\:\.]\s*'+str(j+1)+'\.\s*) ',"",str(claim)).strip() 
				b = '[\']'
				claim = claim.replace(b, "")
				new_ls.extend(['Claim ' + str(j+1), str(claim)])
			
			else:
				#clean all the rest of the claims
				claim=re.sub(r'('+ str(j+1)+'\.\s+)',"",str(claim)).strip()
				claim=re.sub(r'([\"\"])|(\\)|([\'\'])|(\[\]) ',"",str(claim)).strip()
				claim=re.sub(r'\'',"",str(claim)).strip()
				new_ls.extend(['Claim ' + str(j+1), str(claim)])
			
			temp_2.append(new_ls)
		
		temp.extend(temp_2)
		
		list_pat.extend(temp)


	return pd.DataFrame(list_pat, columns = ['Publn_Nr', 'Family_ID', 'Appln_No', 'Appln_Num_Orig','Title', 'Type', 'Text'])

