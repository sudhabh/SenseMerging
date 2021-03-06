#Rada Similarity Measures
import subprocess
from collections import OrderedDict
import operator
import math
import numpy
from numpy import array

#similarity threshold
simi_threshold=0.7
print "Similarity threshold set to ",simi_threshold
print "Loading HWN verb synsets...."
#print "\nCreating idSynsetGlossDict...................."
synsetList={}
idSynsetGlossDict={}
fp=open("../resources/hinwn/data.verb","r")
for line in fp:
	line=line.strip()
	ID=line.split(":~:")[0]
	synsetMembers=line.split(":~:")[-1]	
	temp=[]
	for synsetword in synsetMembers.split(", "):
		if " " in synsetword:
			temp=synsetword.split(" ")
		else:
			temp.append(synsetword)
	synsetList[ID]=temp
	idSynsetGlossDict[int(ID)]="{"+line.split(":~:")[-1]+"} "+line.split(":~:")[2]
fp.close()
#print "Size of HWN verb synsets",len(idSynsetGlossDict)

#print "Loading wordSenseDict...."
wordSenseDict={}
fp=open("../resources/hinwn/verb.idx","r")
for line in fp:
	line=line.strip()
	word=line.split(" ")[0]
	tagList=line.split(" ")[1:]
	wordSenseDict[word]=tagList
fp.close()
#print "Size of HWN verbs: ",len(wordSenseDict)

#print "Loading glosses................"
taggedGlossDict={}
fp_gloss=open("../resources/hinwn/tagged.gloss.txt","r")
for line in fp_gloss:
	line=line.strip()
	Id=line.split("\t")[0]
	wordList=line.split("\t")[1].split(" ")
	temp=[]
	for w in wordList:
		if "_S" not in w:
			temp.append(w)
		#if "_N" in w or "_V" in w or "J" in w:
		#	temp.append(w)
	taggedGlossDict[Id]=temp
fp_gloss.close()
#print "Size of glossDict", len(taggedGlossDict)

#print "Loading TF-IDF of gloss words ..................."
idf={}
fp=open("../resources/glossWithTF-IDFScore.txt","r")
for line in fp:
	line=line.strip()
	idf[line.split("\t")[0]]=int(line.split("\t")[1].split(".")[0])
fp.close()
#print "Size of tagged glosses",len(idf)


print "Loading word vectors...."
vectorList={}
fr_word2vec=open("../resources/leipnigAndBojarICILskip7.txt","r")
for line in fr_word2vec:
	line=line.strip()
	word= line.split(" ")[0]
	v=line.split(" ")[1:]
	vectorList[word]=map(float, v)
print "Size of word vectors=", len(vectorList)

def findRadaSim(S1,S2):
	if S1==S2:
		return 1.0
	else:
		return 0.5*(findSim(S1,S2)+findSim(S2,S1))

def findSim(S1,S2):
	simi=0.0
	avgIDF=0.0
	#print "\n For words from gloss"," ",S1
	for w in taggedGlossDict[S1]:
		#if "_N" in w or "_V" in w or  "J" in w :
		if w.split("_")[0] in idf:
			#print "\t word: ",w
			simi=simi+(maxSim(w,S2)*idf[w.split("_")[0]])
			avgIDF=avgIDF+idf[w.split("_")[0]]
			#print "\tmaxSimi",maxSim(w,S2),"\tidf",idf[w.split("_")[0]]
	if avgIDF!=0.0:
		return simi/avgIDF
	else:
		return 0.0

def maxSim(w1,S):
	maX=0.0
	for w2 in taggedGlossDict[S]:
		simi=cosTheta(w1,w2)
		if simi>maX:
			maX=simi
	return maX
	
def cosTheta(w1,w2):
	if w1==w2:
		return 1.0
	else:
		if w1 in vectorList and w2 in vectorList:
			dotProduct = reduce( operator.add, map( operator.mul, vectorList[w1], vectorList[w2]))
			norm_w1= numpy.linalg.norm(vectorList[w1]) 
			norm_w2= numpy.linalg.norm(vectorList[w2]) 
			return (dotProduct /( norm_w1 * norm_w2))
		else:
			return 0.0

#print "Loading input files ..................."
gold={}
gold_cluster=0
fp=open("../resources/gold_merging3.txt","r")
for line in fp:
	line=line.strip()
	gold[line.split("\t")[0]]=int(line.split("\t")[1])
	if int(line.split("\t")[1])==1:
		gold_cluster=gold_cluster+1
fp.close()
print "Size of gold",len(gold)
print "Total gold clusters",gold_cluster
print "Total gold non-clusters",len(gold)-gold_cluster
correctly_merged=0
incorrectly_merged=0
correctly_non_merged=0
incorrectly_non_merged=0
total_merged=0
total_non_merged=0
total=0 
fw_error=open("error_radaSimilarity.txt","w")
radaSimilarityMatrix={}

print "\nRada Similarity using word2vec...."
for word in gold:
		simi={}
		senses=wordSenseDict[word]
		S1=senses[0]
		S2=senses[1]
		
		similarity=findRadaSim(S1,S2)
		
		if similarity>=simi_threshold:
				if gold[word]==1:
					correctly_merged=correctly_merged+1
					fw_error.write(word+"\t"+str(similarity)+"\n")
				else:
					incorrectly_merged=incorrectly_merged+1
					
					
				total_merged=total_merged+1
		else:
				if gold[word]==0:
					correctly_non_merged=correctly_non_merged+1
				else:
					incorrectly_non_merged=incorrectly_non_merged+1
					

				total_non_merged=total_non_merged+1
p=correctly_merged/float(total_merged)
r=correctly_merged/float(gold_cluster)
print "\n\t\tTotal merged", total_merged		
print "\t\t***************************"
print "\t\tPrecision: ",p
print "\t\tRecall: ",r
print "\t\tF-measure: ",2*p*r/float(p+r)
print "\t\t***************************"

fw_error.close()				
def avgIDF(S1):
	avg=0.0
	#print "\n For words from gloss"," ",S1
	for w in taggedGlossDict[S1]:
		if w.split("_")[0] in idf:
			#print "\t word: ",w
			avg=avg+idf[w.split("_")[0]]
			#print "\tmaxSimi",maxSim(w,S2),"\tidf",idf[w.split("_")[0]]
	return avg

correctly_merged=0
incorrectly_merged=0
correctly_non_merged=0
incorrectly_non_merged=0
total_merged=0
total_non_merged=0
total=0 

print "\nBaseline merging..................."
fw_baseline=open("../resources/baseline_idf.txt","w")
for word in gold:
		fw_baseline.write("\n***********"+word+"***********\n")
		senses=wordSenseDict[word]
		S1=senses[0]
		S2=senses[1]
		matchedWords=list(set(taggedGlossDict[S1]) & set(taggedGlossDict[S2])) 
		commonIDF=0.0
		similarity=0.0
		for w in matchedWords:
			fw_baseline.write(w+"\t")
			if w.split("_")[0] in idf:
				commonIDF=commonIDF+idf[w.split("_")[0]]
		fw_baseline.write(w+"\t"+str(commonIDF)+"\n")
		idf1=avgIDF(S1)
		idf2=avgIDF(S2)
		if idf1!=0.0 and idf2!=0.0:
			similarity=commonIDF*0.5*((1/idf1)+(1/idf2))
		fw_baseline.write(S1+"\t"+S2+"\t"+str(similarity)+"\n")
		
		if similarity>=simi_threshold:
				if gold[word]==1:
					correctly_merged=correctly_merged+1
				else:
					incorrectly_merged=incorrectly_merged+1
				total_merged=total_merged+1
		else:
				if gold[word]==0:
					correctly_non_merged=correctly_non_merged+1
				else:
					incorrectly_non_merged=incorrectly_non_merged+1
				total_non_merged=total_non_merged+1

p=correctly_merged/float(total_merged)
r=correctly_merged/float(gold_cluster)
print "\n\t\tTotal merged", total_merged		
print "\t\t***************************"
print "\t\tPrecision: ",p
print "\t\tRecall: ",r
print "\t\tF-measure: ",2*p*r/float(p+r)
print "\t\t***************************"

fw_baseline.close()

correctly_merged=0
incorrectly_merged=0
correctly_non_merged=0
incorrectly_non_merged=0
total_merged=0
total_non_merged=0
total=0

print "\nPure Baseline merging..................."
fw_baseline=open("../resources/baseline_pure.txt","w")
for word in gold:
		fw_baseline.write("\n***********"+word+"***********\n")
		senses=wordSenseDict[word]
		S1=senses[0]
		S2=senses[1]
		matchedWords=list(set(taggedGlossDict[S1]) & set(taggedGlossDict[S2])) 
		
		similarity=0.0
		fw_baseline.write("\nwords frm S1: "+S1)
		for w in taggedGlossDict[S1]:
			fw_baseline.write(w+"\t")
		fw_baseline.write("\nwords frm S1: "+S2)
		for w in taggedGlossDict[S2]:
			fw_baseline.write(w+"\t")
			
		fw_baseline.write("\nMatched words: ")
		for w in matchedWords:
			fw_baseline.write(w+"\t")
		len_S1=float(len(taggedGlossDict[S1]))
		len_S2=float(len(taggedGlossDict[S2]))
		if len_S1!=0.0 and len_S2!=0.0:
			similarity=0.5*len(matchedWords)*((1/len_S1)+(1/len_S2))
				
		fw_baseline.write(S1+"\t"+S2+"\t"+str(similarity)+"\n")
		
		if similarity>=simi_threshold:
				if gold[word]==1:
					correctly_merged=correctly_merged+1
				else:
					incorrectly_merged=incorrectly_merged+1
				total_merged=total_merged+1
		else:
				if gold[word]==0:
					correctly_non_merged=correctly_non_merged+1
				else:
					incorrectly_non_merged=incorrectly_non_merged+1
				total_non_merged=total_non_merged+1


p=correctly_merged/float(total_merged)
r=correctly_merged/float(gold_cluster)
print "\n\t\tTotal merged", total_merged	
print "\n\t\tCorrectly merged", correctly_merged	
	 	
print "\t\t***************************"
print "\t\tPrecision: ",p
print "\t\tRecall: ",r
print "\t\tF-measure: ",2*p*r/float(p+r)
print "\t\t***************************"


fw_baseline.close()

compo_gold={}
fp=open("../resources/merged.verb2","r")
for line in fp:
	line=line.strip()
	if "txt" not in line and "i" not in line:
		id1=line.split("\t")[1]
		id2=line.split("\t")[2]
		simi=line.split("\t")[3]
		if id1 not in compo_gold:
			temp={}
			temp[id2]=simi
			compo_gold[id1]=temp
		else:
			temp={}
			temp=compo_gold[id1]
			temp[id2]=simi
			compo_gold[id1]=temp
		if id2 not in compo_gold:
			temp={}
			temp[id1]=simi
			compo_gold[id2]=temp
		else:
			temp={}
			temp=compo_gold[id2]
			temp[id1]=simi
			compo_gold[id2]=temp
fp.close()

correctly_merged=0
incorrectly_merged=0

correctly_non_merged=0
incorrectly_non_merged=0

total_merged=0
fw_simi=open("../resources/compoSimilarity.txt","w")	
print "\nCompositional Similarity using word2vec...."
for word in gold:
		simi={}
		
		if gold[word]==1:
			senses=wordSenseDict[word]
			S1=senses[0]
			S2=senses[1]
			if S1 in compo_gold:
				temp=compo_gold[S1]
				if S2 in temp:
					simi=temp[S2]
					simi=float(simi)
					#print word,S1,S2,simi
					if simi<=simi_threshold:	
						correctly_merged=correctly_merged+1
						total_merged=total_merged+1
						
					else:
						incorrectly_non_merged=incorrectly_non_merged+1
						fw_simi.write(word+"\t"+S1+"\t"+S2+"\t"+str(simi)+"\n")
		else:
			senses=wordSenseDict[word]
			S1=senses[0]
			S2=senses[1]
			if S1 in compo_gold:
				temp=compo_gold[S1]
				if S2 in temp:
					simi=temp[S2]
					simi=float(simi)
					#print word,S1,S2,simi
					if simi<=simi_threshold:	
						total_merged=total_merged+1
						incorrectly_merged=incorrectly_merged+1
					else:
						correctly_non_merged=correctly_non_merged+1
						fw_simi.write(word+"\t"+S1+"\t"+S2+"\t"+str(simi)+"\n")
print "Correctly merged",correctly_merged
print "Total merged",total_merged

p=correctly_merged/float(total_merged)
r=correctly_merged/float(gold_cluster)
print "\n\t\tTotal merged", total_merged		
print "\t\t***************************"
print "\t\tPrecision: ",p
print "\t\tRecall: ",r
print "\t\tF-measure: ",2*p*r/float(p+r)
print "\t\t***************************"


fw_simi.close()

wn_simi_threshold=1-simi_threshold
print "WordNet Similarity Threshold....",wn_simi_threshold
