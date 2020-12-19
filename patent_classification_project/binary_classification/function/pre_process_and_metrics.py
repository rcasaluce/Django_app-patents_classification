import pandas as pd

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords


def pre_process_db(dataset):
    
    """
    The function splits the text in tokens,
    eliminates puntaction, numbers and 
    reduces the verbs to their lemma.
    
    Parameters
    ----------
    dataset : dataset merged
    
    Returns
    -------
    The input dataset with a extra column which is the text cleaned 
    
    """
    
    #parse claims
    stop_words = set(stopwords.words('english'))
    word_lemmatizer = WordNetLemmatizer()
    tokenizer = RegexpTokenizer(r'\w+(?:[-\\]\w+)?')#keeps words with hyphen and words back slash (problem it doubles the slash)

    list_num = str(list((range(10))))

    da = []
    for i in range(len(dataset)):

        
        text = dataset['Text'].iloc[i]
        text = tokenizer.tokenize(str(text))
        text =  [x.lower() for x in text]
        for k in range(len(text)):
            if len(text[k]) !=0:
                if text[k][0] in list_num or text[k] in stop_words:
                    #it adds a with space insted of a number or a stop word
                    text[k] = ''
                else:
                    text[k] = word_lemmatizer.lemmatize(text[k], pos="v")
        text = ' '.join(filter(None,text))#filter and None help to elimate white spaces in the list of strings

        da.append(text)   
        
    dataset['text_clean'] = da
        
    return dataset 

def calculate_perc_product_pat(test_data):
    
    """
    
    """

    #creates data frame with two rows with total num of claims 0 and 1s in the other.
    pred_labels = test_data.groupby(by='predicted_label').count().reset_index()

    #keeps only two columns and two rows of the labels and publication numbers
    pred_labels = pred_labels[['predicted_label' , 'Publn_Nr']]
    
    pred_labels.rename(columns = {'Publn_Nr':'nr_claims_x_type'}, inplace = True)

    #for predicted labels it calculate the percentage of a patent being product
    num_claims_pred_labels = 0
    product_pred = 0
    percentage_product_pred_label = 0
   
    
    for j in range(pred_labels.shape[0]):
        
        num_claims_pred_labels += pred_labels['nr_claims_x_type'].loc[j]

        #only if the claim is labelled 1 - PRODUCT 
        if j == 1:
            
            #store the number of claims labelled 0 - product
            product_pred = pred_labels['nr_claims_x_type'].loc[j]
        else:
            product_pred = 0
    
    
    if product_pred != 0:
        
        #calculates the percentage of patent that is product - pred labels
        percentage_product_pred_label = product_pred / num_claims_pred_labels 
        
    else:
        percentage_product_pred_label = 1
    
    percentage_product_pred_label = f'{round((percentage_product_pred_label * 100), 2)}%'
    
    return percentage_product_pred_label 
