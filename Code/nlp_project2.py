# -*- coding: utf-8 -*-
"""nlp_project2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15zQVzPXSrkJhkIRD0yXW3wrFg7QzaLNe

Main module to run the code
"""

from __future__ import division
from urllib.request import urlopen 
import nltk
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
from nltk.stem import WordNetLemmatizer 
from nltk import pos_tag
import numpy as np
import time
import sys
from nltk.tokenize import word_tokenize 
from nltk.corpus import wordnet
from nltk.tokenize.treebank import TreebankWordDetokenizer
import ssl
from itertools import chain
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
train_url="https://www.hlt.utdallas.edu/~moldovan/CS6320.20S/modified_train.txt"
test_url="https://www.hlt.utdallas.edu/~moldovan/CS6320.20S/modified_test.txt"
"""Read the train and test file from the url"""

def read_file_from_url(url):
  corpse=[]
  corpse_tags=[]
  #create an unverified context so that  certificate verification doesn't happen
  context = ssl._create_unverified_context()
  with urlopen(url,context=context) as url_content:
    i=0
    sentence=[]
    tage=[]
    for line in url_content:
        line = line.decode('utf-8')
        line_split=line.split()
        if '-DOCSTART-' in line_split:
           continue
        else:
           if len(line_split)==0:
              if len(sentence) and len(tags)>0:
                 corpse.append(sentence)
                 corpse_tags.append(tags)
              sentence=[]
              tags=[]
              continue
           else:
              for i in range(0,len(line_split)-1):
                  sentence.append(line_split[i])
              tags.append(line_split[len(line_split)-1])
    corpse.append(sentence)
    corpse_tags.append(tags)           
    #print ("The number of sentences in the corpus is",len(corpse))  
    return (corpse,corpse_tags)

"""Calculate the number of unique tokens and tags in the training set"""

def calculate_unique_tokens_and_tags(corpse,tag):
    unique_tokens=list(set(chain(*corpse)))
    unique_tags=list(set(chain(*tag)))
    #print ("The number of unique tokens is",len(unique_tokens))
    #print ("The number of unique tags is",len(unique_tags))
    return unique_tokens,unique_tags

"""Convert the entire corpus tokens to lower case"""

def convert_lowercase(corpse):
    corpse_lc=[]
    for i in range(0,len(corpse)):
        corpse_lc.append(list(map(lambda x: x.lower(), corpse[i]))) 
    return corpse_lc

"""Convert a tuple to dictionary"""

def convert_map_to_dict(tag_map):
    tag_encode_dict={}
    for j in range(0,len(tag_map)):
        tag_encode_dict[tag_map[j][1]]=tag_map[j][0]
    return tag_encode_dict

"""Convert the tags to integer identifier using the mapping defined in the dictionaries"""

def replace_tags_by_int(tag,tag_dict):
    for i in range(0,len(tag)):
        tag_sentence=tag[i]
        for j in range(0,len(tag_sentence)):
            tag_sentence[j]=tag_dict[tag_sentence[j]]
    return tag

"""extract lemmas from sentences"""

def extract_lemmas_and_POS(train_corpus):
    train_corpus_POS=[]
    train_corpus_lemmatize=[]
    all_lemmas=[]
    all_POS=[]
    for i in range(0,len(train_corpus)): 
        token_POS=pos_tag(train_corpus[i])
        train_corpus_POS.append(token_POS)

        # Populate all the POS taggers generated
        for j in range(0,len(token_POS)):
            all_POS.append(token_POS[j][1]) 
        word_list=train_corpus[i]
        lemmatizer=WordNetLemmatizer()
        word_lemmatized= [lemmatizer.lemmatize(w,penbank_to_wordnet_POS(w)) for w in word_list]
        for lemmas in word_lemmatized:
            all_lemmas.append(lemmas)
        train_corpus_lemmatize.append(word_lemmatized)    
    #print ("The POS and lemmatize lengths are", len(train_corpus_POS),len(train_corpus_lemmatize))
    print ("No. of all lemmas and POS", len(all_lemmas),len(all_POS))
    return (train_corpus_POS,train_corpus_lemmatize,all_POS,all_lemmas)

"""Convert Penbank POS tagger to word net POS tagger"""

def penbank_to_wordnet_POS(word):
    tag_first_letter=pos_tag([word])[0][1][0].upper()
    pen_to_wordnet_dict = {"J": wordnet.ADJ,"N": wordnet.NOUN,"V": wordnet.VERB,"R": wordnet.ADV}
    return pen_to_wordnet_dict.get(tag_first_letter, wordnet.NOUN)

"""Convert POS and lemma to dict"""

def convert_to_dict(word_unique,identifier):
    word_dict={}
    idx=0
    for i in range(0,len(word_unique)):
        word_dict[word_unique[i]]=idx
        idx=idx+1
    if identifier=="lemma": 
       word_dict['UNK']=idx
    return word_dict

"""Create train and test feature vectors"""

def create_feature_vectors(train_corpus_lemma,all_lemmas_unique,lemma_dict,train_corpus_POS,all_POS_unique,POS_dict,train_tag_encode):
    feat=[]
    #label=[]
    lemma_feat=[]
    pos_feat=[]
    #print("The length of lemma dict is",len(lemma_dict))
    #Creating a feature vector of lemma 
    for i in range(0,len(train_corpus_lemma)):
        sentence=train_corpus_lemma[i]
        for j in sentence:
            lemma_feat_sentence=np.zeros(len(lemma_dict))
            if j  in all_lemmas_unique:
               index=lemma_dict[j]
            else:
               index=lemma_dict['UNK']   
            lemma_feat_sentence[index]=1
            lemma_feat.append(lemma_feat_sentence)
    lemma_feat=np.asarray(lemma_feat)
    #print ("The shape of lemma_feat is", lemma_feat.shape)

    #Creating a feature vector of the POS
    for i in range(0,len(train_corpus_POS)):
        sentence=train_corpus_POS[i]
        for j in range(0,len(sentence)):
            pos_feat_sentence=np.zeros(len(POS_dict))
            if sentence[j][1] in all_POS_unique:
               index=POS_dict[sentence[j][1]]
            else:
               index=POS_dict['UNK']
            pos_feat_sentence[index]=1
            pos_feat.append(pos_feat_sentence)
    pos_feat=np.asarray(pos_feat)
    #print ("The shape of pos_feat is",pos_feat.shape)
    feat=np.hstack((lemma_feat,pos_feat))
    print ("The shape of feature vector is", feat.shape)     
    #Creating the labels
    label = [item for sublist in train_tag_encode for item in sublist]
    label=np.asarray(label)
    print ("The shape of label is", label.shape)
    return feat,label

if __name__ == "__main__":	
	#TASK-1: DATA PREPROCESSIG
	train_corpse,train_tag=read_file_from_url(train_url)
	test_corpse,test_tag=read_file_from_url(test_url)
	unique_train_tokens,unique_tag=calculate_unique_tokens_and_tags(train_corpse,train_tag)
	print ("No. of unique tokens,tags,train sentences,test senteces  are",len(unique_train_tokens),len(unique_tag),len(train_corpse),len(test_corpse))
	train_corpse_lc=convert_lowercase(train_corpse)
	#print (len(train_corpse))
	test_corpse_lc=convert_lowercase(test_corpse)
	tag_encode_map=list(enumerate(unique_tag))
	tag_encode_dict=convert_map_to_dict(tag_encode_map)
	#print (tag_encode_dict)
	train_tag_encode=replace_tags_by_int(train_tag,tag_encode_dict)
	test_tag_encode=replace_tags_by_int(test_tag,tag_encode_dict)
	#TASK-2: FEATURE ENGINEERING
	train_corpus_POS,train_corpus_lemma,all_POS,all_lemmas=extract_lemmas_and_POS(train_corpse_lc)
	test_corpus_POS,test_corpus_lemma,all_POS_test,all_lemmas_test=extract_lemmas_and_POS(test_corpse_lc)
	all_POS_unique= list(set(all_POS))
	print ("No. of unique POS tags",len(all_POS_unique))
	all_lemmas_unique=list(set(all_lemmas))
	print ("No. of unique lemmas are", len(all_lemmas_unique))
	lemma_dict=convert_to_dict(all_lemmas_unique,"lemma")
	POS_dict=convert_to_dict(all_POS_unique,"pos")
	Xtrain,ytrain=create_feature_vectors(train_corpus_lemma,all_lemmas_unique,lemma_dict,train_corpus_POS,all_POS_unique,POS_dict,train_tag_encode)
	Xtest,ytest=create_feature_vectors(test_corpus_lemma,all_lemmas_unique,lemma_dict,test_corpus_POS,all_POS_unique,POS_dict,test_tag_encode)
	#TASK-3: LEARNING THE MODEL
	model = LogisticRegression(random_state=0).fit(Xtrain, ytrain)
	start = time.time()
	ypredict=model.predict(Xtest)
	end = time.time()
	test_size=379477
	print ("The throughput is", (test_size/(end-start))/(1000))
	print ("The size of the test set is",test_size)
	print ("The inference time to make predictions", end-start)
	#Reporting the relevant metric
	print("Accuracy:",accuracy_score(ytest,ypredict))
	print("Recall:",recall_score(ytest,ypredict,average='micro'))
	print("F1 score:",f1_score(ytest,ypredict,average='micro'))
	print("Precision:",precision_score(ytest,ypredict,average='micro'))
