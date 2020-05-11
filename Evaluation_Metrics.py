# -*- coding: utf-8 -*-
"""Untitled24.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jEPtsQiPDg1DflM4xsTq0oZ-MKw6HNkM
"""

import nltk
nltk.download('punkt')

import nltk
nltk.download('stopwords')

from nltk.stem.porter import PorterStemmer
from nltk.corpus import wordnet
from itertools import chain, product

def meteor_score(
    references,
    hypothesis,
    preprocess=str.lower,
    stemmer=PorterStemmer(),
    wordnet=wordnet,
    alpha=0.9,
    beta=3,
    gamma=0.5,
):
    return max(
        [
            meteor_score(
                reference,
                hypothesis,
                stemmer=stemmer,
                wordnet=wordnet,
                alpha=alpha,
                beta=beta,
                gamma=gamma,
            )
            for reference in references
        ]
    )

>>> import nltk
  >>> nltk.download('wordnet')

# Meteor

from nltk.stem.porter import PorterStemmer
from nltk.corpus import wordnet
from itertools import chain, product


def _generate_enums(hypothesis, reference, preprocess=str.lower):
    hypothesis_list = list(enumerate(preprocess(hypothesis).split()))
    reference_list = list(enumerate(preprocess(reference).split()))
    return hypothesis_list, reference_list


def exact_match(hypothesis, reference):
    hypothesis_list, reference_list = _generate_enums(hypothesis, reference)
    return _match_enums(hypothesis_list, reference_list)



def _match_enums(enum_hypothesis_list, enum_reference_list):
    word_match = []
    for i in range(len(enum_hypothesis_list))[::-1]:
        for j in range(len(enum_reference_list))[::-1]:
            if enum_hypothesis_list[i][1] == enum_reference_list[j][1]:
                word_match.append(
                    (enum_hypothesis_list[i][0], enum_reference_list[j][0])
                )
                (enum_hypothesis_list.pop(i)[1], enum_reference_list.pop(j)[1])
                break
    return word_match, enum_hypothesis_list, enum_reference_list


def _enum_stem_match(
    enum_hypothesis_list, enum_reference_list, stemmer=PorterStemmer()
):
    stemmed_enum_list1 = [
        (word_pair[0], stemmer.stem(word_pair[1])) for word_pair in enum_hypothesis_list
    ]

    stemmed_enum_list2 = [
        (word_pair[0], stemmer.stem(word_pair[1])) for word_pair in enum_reference_list
    ]

    word_match, enum_unmat_hypo_list, enum_unmat_ref_list = _match_enums(
        stemmed_enum_list1, stemmed_enum_list2
    )

    enum_unmat_hypo_list = (
        list(zip(*enum_unmat_hypo_list)) if len(enum_unmat_hypo_list) > 0 else []
    )

    enum_unmat_ref_list = (
        list(zip(*enum_unmat_ref_list)) if len(enum_unmat_ref_list) > 0 else []
    )

    enum_hypothesis_list = list(
        filter(lambda x: x[0] not in enum_unmat_hypo_list, enum_hypothesis_list)
    )

    enum_reference_list = list(
        filter(lambda x: x[0] not in enum_unmat_ref_list, enum_reference_list)
    )

    return word_match, enum_hypothesis_list, enum_reference_list


def stem_match(hypothesis, reference, stemmer=PorterStemmer()):
    enum_hypothesis_list, enum_reference_list = _generate_enums(hypothesis, reference)
    return _enum_stem_match(enum_hypothesis_list, enum_reference_list, stemmer=stemmer)



def _enum_wordnetsyn_match(enum_hypothesis_list, enum_reference_list, wordnet=wordnet):
    word_match = []
    for i in range(len(enum_hypothesis_list))[::-1]:
        hypothesis_syns = set(
            chain(
                *[
                    [
                        lemma.name()
                        for lemma in synset.lemmas()
                        if lemma.name().find("_") < 0
                    ]
                    for synset in wordnet.synsets(enum_hypothesis_list[i][1])
                ]
            )
        ).union({enum_hypothesis_list[i][1]})
        for j in range(len(enum_reference_list))[::-1]:
            if enum_reference_list[j][1] in hypothesis_syns:
                word_match.append(
                    (enum_hypothesis_list[i][0], enum_reference_list[j][0])
                )
                enum_hypothesis_list.pop(i), enum_reference_list.pop(j)
                break
    return word_match, enum_hypothesis_list, enum_reference_list


def wordnetsyn_match(hypothesis, reference, wordnet=wordnet)
    enum_hypothesis_list, enum_reference_list = _generate_enums(hypothesis, reference)
    return _enum_wordnetsyn_match(
        enum_hypothesis_list, enum_reference_list, wordnet=wordnet
    )



def _enum_allign_words(
    enum_hypothesis_list, enum_reference_list, stemmer=PorterStemmer(), wordnet=wordnet
):
    exact_matches, enum_hypothesis_list, enum_reference_list = _match_enums(
        enum_hypothesis_list, enum_reference_list
    )

    stem_matches, enum_hypothesis_list, enum_reference_list = _enum_stem_match(
        enum_hypothesis_list, enum_reference_list, stemmer=stemmer
    )

    wns_matches, enum_hypothesis_list, enum_reference_list = _enum_wordnetsyn_match(
        enum_hypothesis_list, enum_reference_list, wordnet=wordnet
    )

    return (
        sorted(
            exact_matches + stem_matches + wns_matches, key=lambda wordpair: wordpair[0]
        ),
        enum_hypothesis_list,
        enum_reference_list,
    )


def allign_words(hypothesis, reference, stemmer=PorterStemmer(), wordnet=wordnet):
    enum_hypothesis_list, enum_reference_list = _generate_enums(hypothesis, reference)
    return _enum_allign_words(
        enum_hypothesis_list, enum_reference_list, stemmer=stemmer, wordnet=wordnet
    )



def _count_chunks(matches):
    i = 0
    chunks = 1
    while i < len(matches) - 1:
        if (matches[i + 1][0] == matches[i][0] + 1) and (
            matches[i + 1][1] == matches[i][1] + 1
        ):
            i += 1
            continue
        i += 1
        chunks += 1
    return chunks


def single_meteor_score(
    reference,
    hypothesis,
    preprocess=str.lower,
    stemmer=PorterStemmer(),
    wordnet=wordnet,
    alpha=0.9,
    beta=3,
    gamma=0.5,
):
    enum_hypothesis, enum_reference = _generate_enums(
        hypothesis, reference, preprocess=preprocess
    )
    translation_length = len(enum_hypothesis)
    reference_length = len(enum_reference)
    matches, _, _ = _enum_allign_words(enum_hypothesis, enum_reference, stemmer=stemmer)
    matches_count = len(matches)
    try:
        precision = float(matches_count) / translation_length
        recall = float(matches_count) / reference_length
        fmean = (precision * recall) / (alpha * precision + (1 - alpha) * recall)
        chunk_count = float(_count_chunks(matches))
        frag_frac = chunk_count / matches_count
    except ZeroDivisionError:
        return 0.0
    penalty = gamma * frag_frac ** beta
    return (1 - penalty) * fmean



def meteor_score(
    references,
    hypothesis,
    preprocess=str.lower,
    stemmer=PorterStemmer(),
    wordnet=wordnet,
    alpha=0.9,
    beta=3,
    gamma=0.5,
):
    return max(
        [
            single_meteor_score(
                reference,
                hypothesis,
                stemmer=stemmer,
                wordnet=wordnet,
                alpha=alpha,
                beta=beta,
                gamma=gamma,
            )
            for reference in references
        ]
    )

"""# **ROUGE SCORE CALCULATION**"""

pip install py-rouge

myfile=open("results.txt","r+")
f=myfile.readlines()
for ele in f:
    resultList=ele.split(",")

# ROUGE 
import rouge
import nltk
nltk.download('punkt')


def prepare_results(p, r, f):
    return '\t{}:\t{}: {:5.2f}\t{}: {:5.2f}\t{}: {:5.2f}'.format(metric, 'P', 100.0 * p, 'R', 100.0 * r, 'F1', 100.0 * f)


for aggregator in ['Avg', 'Individual']:
    print('Evaluation with {}'.format(aggregator))
    apply_avg = aggregator == 'Avg'

    evaluator = rouge.Rouge(metrics=['rouge-n', 'rouge-l', 'rouge-w'],
                           max_n=4,
                           limit_length=True,
                           length_limit=100,
                           length_limit_type='words',
                           apply_avg=apply_avg,
                          #  apply_best=apply_best,
                           alpha=0.5, # Default F1_score
                           weight_factor=1.2,
                           stemming=True)

    scores = evaluator.get_scores(realValue, predictedValue)

    for metric, results in sorted(scores.items(), key=lambda x: x[0]):
        if not apply_avg: # value is a type of list as we evaluate each summary vs each reference
            for hypothesis_id, results_per_ref in enumerate(results):
                nb_references = len(results_per_ref['p'])
                # for reference_id in range(nb_references):
                #     print('\tHypothesis #{} & Reference #{}: '.format(hypothesis_id, reference_id))
                #     print('\t' + prepare_results(results_per_ref['p'][reference_id], results_per_ref['r'][reference_id], results_per_ref['f'][reference_id]))
            print()
        else:
            print(prepare_results(results['p'], results['r'], results['f']))
    print()

resultList[1]

resultList[0]
imageName=[]
realValue=[]
predictedValue=[]

for i in range(0,len(resultList)):
    if(i%2==0):
        imageName.append(resultList[i].split(':')[0])
        realValue.append(resultList[i].split(':')[1])
    else:
        predictedValue.append(resultList[i])

"""# **`METEOR SCORE CALCULATION`**"""

avg_ms=0
score_list=[]
list1m=[]
list2m=[]
list3m=[]
list4m=[]
list5m=[]
list6m=[]
for i in range(0,len(realValue)):
  accuracy=(round(single_meteor_score(predictedValue[i],realValue[i]),4))
  if(accuracy>=0.6):
    list1m.append(imageName[i])
  elif(accuracy>=0.5 and accuracy<0.6):
    list2m.append(imageName[i])
  elif(accuracy>=0.4 and accuracy<0.5):
    list3m.append(imageName[i])
  elif(accuracy>=0.3 and accuracy<0.4):
    list4m.append(imageName[i])
  elif(accuracy>=0.2 and accuracy<0.3):
    list5m.append(imageName[i])
  else:
    list6m.append(imageName[i])
  score_list.append(accuracy)
avg_ms=(0.65*3) + (0.55*8) +(0.45*43) + (0.35*125) + (0.25*255)+ (0.15*901)
print("Meteor Score is - ->",avg_ms/1335)
print(score_list)

print(list1m)
print(len(list1m))

print(list2m)
print(len(list2m))

print(list3m)
print(len(list3m))

print(list4m)
print(len(list4m))

print(list5m)
print(len(list5m))

len(list4b)



"""# **BLEU SCORE**"""

word_list=['over','the','of','there','are','and','is','for','<start>','<end>']
list1b=[]
list2b=[]
list3b=[]
list4b=[]
list5b=[]
m=0
for i in range(0,len(realValue)):
    real_list=realValue[i].split()
    predicted_list=predictedValue[i].split()
    real_new=[]
    predicted_new=[]
    for j in real_list:
        if j not in word_list:
            real_new.append(j)
    for j in predicted_list:
        if j not in word_list:
            predicted_new.append(j)
    real_string=""
    predicted_string=""
    for ele in real_new:
        real_string=real_string+ele+" "
    for ele in predicted_new:
        predicted_string=predicted_string+ele+" "
    documents=[real_string,predicted_string]
    BLEUscore = nltk.translate.bleu_score.sentence_bleu([real_new],predicted_new,weights = (1,0,0,0))
    accuracy=BLEUscore
    if(accuracy>=0.1 and accuracy<0.2):
        list1b.append(imageName[i])
    elif(accuracy>=0.2 and accuracy<0.3):
        list2b.append(imageName[i])
    elif(accuracy>=0.3 and accuracy<0.4):
        list3b.append(imageName[i])
    elif(accuracy>=0.4):
        list4b.append(imageName[i])
    else:
        list5b.append(imageName[i])
    if(BLEUscore>m):
        m=BLEUscore
print(m)

"""# **Cosine Similarity**"""

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

myfile=open("results.txt","r+")
f=myfile.readlines()
for ele in f:
    resultList=ele.split(",")

resultList[0]
imageName=[]
realValue=[]
predictedValue=[]

for i in range(0,len(resultList)):
    if(i%2==0):
        imageName.append(resultList[i].split(':')[0])
        realValue.append(resultList[i].split(':')[1])
    else:
        predictedValue.append(resultList[i])

word_list=['over','the','of','there','are','and','is','for','<start>','<end>']
list1=[]
list2=[]
list3=[]
list4=[]
list5=[]
for i in range(0,len(realValue)):
    real_list=realValue[i].split()
    predicted_list=predictedValue[i].split()
    real_new=[]
    predicted_new=[]
    for j in real_list:
        if j not in word_list:
            real_new.append(j)
    for j in predicted_list:
        if j not in word_list:
            predicted_new.append(j)
    real_string=""
    predicted_string=""
    for ele in real_new:
        real_string=real_string+ele+" "
    for ele in predicted_new:
        predicted_string=predicted_string+ele+" "
    documents=[real_string,predicted_string]
    count_vectorizer = CountVectorizer(stop_words='english')
    count_vectorizer = CountVectorizer()
    sparse_matrix = count_vectorizer.fit_transform(documents)
    doc_term_matrix = sparse_matrix.todense()
    df = pd.DataFrame(doc_term_matrix, 
                      columns=count_vectorizer.get_feature_names(), 
                      index=['real', 'predict'])
    accuracy=cosine_similarity(df,df)[0][1]
    if(accuracy>=0.5 and accuracy<0.6):
        list1.append(imageName[i])
    elif(accuracy>=0.6 and accuracy<0.7):
        list2.append(imageName[i])
    elif(accuracy>=0.7 and accuracy<0.8):
        list3.append(imageName[i])
    elif(accuracy>=0.8):
        list4.append(imageName[i])
    else:
        list5.append(imageName[i])

list_m = list1m.append(list2m)

print(intersection(list2, list1m))

print(intersection(list4, list1m))

print(intersection(list2, list2m))

print(intersection(list1, list2m))

print(intersection(list5,list2m))

def Union(lst1, lst2): 
    final_list = list(set(lst1) | set(lst2)) 
    return final_list

print(intersection(list2m,list4b))
