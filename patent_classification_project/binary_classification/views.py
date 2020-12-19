from django.shortcuts import render
from django.http import Http404
from .predict import *

def home(request):
	if request.method == 'GET':
		return(render(request,'binary_classification/index.html'))
		
	if request.method == 'POST':
		pub_num =  request.POST['Publn_nr']
		
		result, dictionary, url = predict(pub_num)
		
		if dictionary == "" and url == "":#when a patent from USPTO is not found
	
			return render(request,'binary_classification/index.html',{"result":result})
		
		elif dictionary == "" and url != "":#when the claism of an USPTO patent could not be split correctly
			
			return render(request,'binary_classification/index.html',{"result":result, 'url' : url})
			
		else:#when the patents are found for both patent offices
			return render(request,'binary_classification/index.html',{"result":result, "dictionary" : dictionary})
			
	
def info(request):#open the info page
    return render(request,'binary_classification/info.html')


