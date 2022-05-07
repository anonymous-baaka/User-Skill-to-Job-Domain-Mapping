import itertools
import operator
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User,auth
from django.contrib import messages
import logging

from wordcloud import STOPWORDS
from .forms import Resume, ResumeForm, apti_questionForm, tech_questionForm, soft_questionForm
from django.core.files.storage import FileSystemStorage
from .models import apti_question, tech_question, soft_question
import math
#import resumeParser
import os
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import PDFPageAggregator
from pdfminer3.converter import TextConverter
import io
import re
import docx
import pandas as pd
import spacy
import glob
import gensim
import pickle
import sklearn
import random

class Domain_Probability:
    def __init__(self,domain,prob) -> None:
        self.domain=domain
        self.probability=prob


# global
questionList = []
skillist=[]
user_extracted_skills=[]
skillListMap={}
domainIndexArray=['Data Analytics', 'animation', 'backend', 'cisco',
       'data scientist', 'database', 'dot-net', 'java dev',
       'network engineer', 'python dev', 'sql engineer', 'system admin',
       'tester', 'ui/ux dev', 'web dev']

allResults={
   'apti':{
        'score':0,
        'correct':0,
        'wrong':0,
       'apti_tags':{
       "Quantative Aptitude": 0,
        "Verbal Reasoning": 0,
        "Logical Reasoning": 0
       }
   },
   'tech':{
       'score':0,
        'correct':0,
        'wrong':0,
       'tech_tags':
        {
        "dbms": 0,
        "dsa": 0,
        "webd": 0,
        "oops": 0,
        "cn": 0
        }
   },
   'soft':{
       'score':0,
        'correct':0,
        'wrong':0,
       'soft_tags':
       {
           "ss": 0
       }
   }
}

testsTaken={
    'apti':0,
    'tech':0,
    'soft':0
}

isResumeUploaded=False
# Create your views here

def index(request):
    global skillist
    global skillListMap
    skillist=open('skilllist.txt','r')
    s=''
    for ele in skillist:
        s+=ele
    skillist=s
    skillist=skillist.split('$')

    del skillist[0]
    toremove= ['domain', 'software developer / sr. software developer â€“ asp. net', 'lead engineer â€“ voice operations',"['']"]
    for ele in skillist:
        if ele in toremove:
            skillist.remove(ele)

    for i in range(len(skillist)):
        skillListMap[skillist[i]]=i

    return render(request, 'index.html')

def login(request):
    if request.method == "POST":
        username = request.POST['name_Username']
        password = request.POST['name_password']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            messages.info(request, "Credentials invalid ")
            return redirect('login')

    return render(request, 'login.html')

def signup(request):
    messages.info(request, "")
    if request.method == 'POST':
        username = request.POST['name_fullname']
        email = request.POST['name_email']
        password = request.POST['name_pwd']
        passwordre = request.POST['name_pwdre']
        # termsNcondtions=request.POST['name_termsNcondtions']

        if password == passwordre:
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email already used")
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, "username already used")
                return redirect('signup')
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password)
                user.save()
            return redirect('login')
        else:
            messages.info(request, "Passwords do not match")
            return redirect('signup')

    return render(request, 'signup.html')

def quiz(request):
    return render(request, 'dashboard.html')


def logout(request):
    auth.logout(request)
    return redirect('/')

def apti(request):
    #q=apti_question(question="question 1 sadasdfasf",answer="answer 1",option1='a',option2='a',option3='a',option4='a',tag='a')
    # q.save()
    global questionList
    questionList=apti_question.objects.all()
    for q in questionList:
        print("question={} \nans={}".format(q.question, q.answer))
    
    apti_tags = {
        "Quantative Aptitude": 0,
        "Verbal Reasoning": 0,
        "Logical Reasoning": 0,
    }
    #random start
    tagWiseQuestions=[]
    for tag in apti_tags:
        tg1=[]
        for question in questionList:
            print('question.tag= ',question.tag)
            if question.tag == tag:
                print("tag found")
                tg1.append(question)
        tagWiseQuestions.append(tg1)

    questionList=[]
    for tg in tagWiseQuestions:
        questionList.append(random.sample(tg,3))
    #flatten list 
    questionList=list(itertools.chain.from_iterable(questionList))

    return render(request, 'apti.html', {'questionList': questionList})

def uploadResume(request):
    context = {}
    msg = ""
    fail = ""
    #messages.info(request,"upload called")
    if request.method == 'POST':

        form = ResumeForm(request.POST, request.FILES)
        form.Meta.fields
        if form.is_valid():
            #del prev resumes
            print("cwd= ", os.getcwd())
            files=glob.glob(os.getcwd()+"\\uploads\\resume\\*",recursive=True)
            print("===============\n\npath=",files)
            for f in files:
                try:
                    os.remove(f)
                except OSError as e:
                    print("Error: %s - %s." % (e.filename, e.strerror))

            msg = "Resume uploaded Sucessfully"
            form.save()

            global isResumeUploaded
            isResumeUploaded=True

            parseResume()
            return render(request, 'dashboard.html', {'form': form, 'msg': msg})

        else:
            return render(request, 'dashboard.html', {'form': form, 'msg': msg})
    else:
        form = ResumeForm()
        msg = ''
        return render(request, 'dashboard.html', {'form': form, 'msg': msg})

def apti_result(request):
    '''tmp=request.POST.get("id")
    print("\n=======tmp= ",tmp)
    print()'''
    apti_tags = {
        "Quantative Aptitude": 0,
        "Verbal Reasoning": 0,
        "Logical Reasoning": 0,
    }
    correct = 0
    wrong = 0
    score = 0

    if request.method == 'POST':
        for q in questionList:
            userAnswer = request.POST.get("id"+str(q.id))
            print("\n=======userAnswer= ", userAnswer)
            print("\n=======q.answer= ", q.answer)
            if userAnswer == q.answer:
                print("\n=======correct answer")
                correct += 1
                apti_tags[q.tag] += 1
            else:
                if userAnswer == None:
                    print("\n=======user did not answer")
                else:
                    print("\n=======wrong answer")
                    wrong += 1
        score = math.trunc(correct*100/len(questionList))

        print("\n tag=========", apti_tags)
        result = {'correct': correct, 'wrong': wrong,
                  'score': score, 'apti_tags': apti_tags}
        global allResults
        allResults['apti']=result

        #set answered=true
        global testsTaken
        testsTaken['apti']=1
        return render(request, 'dashboard.html')#, {'result': result})
    else:
        return render(request, 'dashboard.html')

#Results page

def result(request):
    global allResults
    topThreeDomains,labels,dataset=generateResult()
    labels0=labels[topThreeDomains[0].domain][:10]
    labels1=labels[topThreeDomains[1].domain][:10]
    labels2=labels[topThreeDomains[2].domain][:10]

    dataset0=dataset[topThreeDomains[0].domain][:10]
    dataset1=dataset[topThreeDomains[1].domain][:10]
    dataset2=dataset[topThreeDomains[2].domain][:10]

    topThreeDomainsDict={}
    domainList=[]
    probList=[]
    for ele in topThreeDomains:
        topThreeDomainsDict[ele.domain]=ele.probability
        domainList.append(ele.domain)
        probList.append(str(1-1/ele.probability))

    #strip preceding zeros from probability array
    '''for i in range(len(probList)):
        ##number of zeros after decimal
        zeros=0
        for j in range(len(2,probList[i])):
            if probList[i][j]=='0':
                zeros+=1
            else:
                break
        if zeros>2:
            probList[i]='0.'+probList[i][1+zeros:]'''

    dom0=[]
    dom0.append(domainList[0])
    dom1=[]
    dom1.append(domainList[1])
    dom2=[]
    dom2.append(domainList[2])

    prob0=[]
    prob0.append(probList[0])
    prob1=[]
    prob1.append(probList[1])
    prob2=[]
    prob2.append(probList[2])

    global testsTaken
    global isResumeUploaded

    if isResumeUploaded==False:
        messages.error(request,"Please upload resume")
        return render(request, 'dashboard.html')
    for key,value in testsTaken.items():
        if value==0:
            print("==========value = 0==========")
            messages.error(request,'Please complete the test for '+key)
            return render(request, 'dashboard.html')

    return render(request,'result.html',
    {'allResults':allResults,
        'topThreeDomainsDict':topThreeDomainsDict,

        'domain0':dom0,'domain1':dom1,'domain2':dom2,
        'prob0':prob0,'prob1':prob1,'prob2':prob2,

        'label0':labels0,'label1':labels1,'label2':labels2,
        'dataset0':dataset0,'dataset1':dataset1,'dataset2':dataset2
        })

# TECH SECTION STARTED
def tech(request):
    global questionList
    tech_tags = {
        "dbms": 0,
        "dsa": 0,
        "webd": 0,
        "oops": 0,
        "cn": 0,
    }
    #randomise questions
    tagWiseQuestions=[]
    questionList = tech_question.objects.all()
    for tag in tech_tags:
        tg1=[]
        for question in questionList:
            if question.tag == tag:
                tg1.append(question)
        tagWiseQuestions.append(tg1)

    questionList=[]
    for tg in tagWiseQuestions:
        questionList.append(random.sample(tg,5))
    #flatten list 
    questionList=list(itertools.chain.from_iterable(questionList))
    
    #random questions end

    for q in questionList:
        print("question={} \nans={}".format(q.question, q.answer))

    return render(request, 'tech.html', {'questionList': questionList})
    # return render(request,'tech.html')

def tech_result(request):
    '''tmp=request.POST.get("id")
    print("\n=======tmp= ",tmp)
    print()'''
    tech_tags = {
        "dbms": 0,
        "dsa": 0,
        "webd": 0,
        "oops": 0,
        "cn": 0,
    }
    correct = 0
    wrong = 0
    score = 0

    if request.method == 'POST':
        for q in questionList:
            userAnswer = request.POST.get("id"+str(q.id))
            print("\n=======userAnswer= ", userAnswer)
            print("\n=======q.answer= ", q.answer)
            if userAnswer == q.answer:
                print("\n=======correct answer")
                correct += 1
                tech_tags[q.tag] += 1
            else:
                if userAnswer == None:
                    print("\n=======user did not answer")
                else:
                    print("\n=======wrong answer")
                    wrong += 1
        score = math.trunc(correct*100/len(questionList))


        print("\n tag=========", tech_tags)
        result = {'correct': correct, 'wrong': wrong,
                  'score': score, 'tech_tags': tech_tags}
        global allResults
        allResults['tech']=result
        
        global testsTaken
        testsTaken['tech']=1
        return render(request, 'dashboard.html')#, {'result': result})
    else:
        return render(request, 'dashboard.html')
    # return render(request, 'tech_result.html')

# SOFT SKILLS
def soft(request):
    global questionList
    questionList = soft_question.objects.all()
    #print("type=\n",type(questionList))
    tmp=[]
    for ele in questionList:
        tmp.append(ele)
    questionList=random.sample(tmp,3)

    for q in questionList:
        print("question={} \nans={}".format(q.question, q.answer))

    return render(request, 'soft.html', {'questionList': questionList})

def soft_result(request):

    '''tmp=request.POST.get("id")
    print("\n=======tmp= ",tmp)
    print()'''
    soft_tags = {
        "ss": 0,
    }
    correct = 0
    wrong = 0
    score = 0

    if request.method == 'POST':

        for q in questionList:
            userAnswer = request.POST.get("id"+str(q.id))
            print("\n=======userAnswer= ", userAnswer)
            print("\n=======q.answer= ", q.answer)
            if userAnswer == q.answer:
                print("\n=======correct answer")
                correct += 1
                soft_tags[q.tag] += 1
            else:
                if userAnswer == None:
                    print("\n=======user did not answer")
                else:
                    print("\n=======wrong answer")
                    wrong += 1
        score = math.trunc(correct*100/1)

        print("\n tag=========", soft_tags)
        result = {'correct': correct, 'wrong': wrong,
                  'score': score, 'soft_tags': soft_tags}
        global allResults
        allResults['soft']=result
        global testsTaken
        testsTaken['soft']=1
        return render(request, 'dashboard.html')#, {'result': result})
    else:
        return render(request, 'dashboard.html')
    # return render(request, 'tech_result.html')

def parseResume():
    #projectDir = 'D:/Projects/Extraction-of-Skills-master'
    projectDir = os.getcwd()
    resumeDir = projectDir + '\\uploads\\resume'
    #print("dir= ",resumeDir)
    global user_extracted_skills

    def convert_pdf_to_txt(path):
        resource_manager = PDFResourceManager()
        fake_file_handle = io.StringIO()
        converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
        page_interpreter = PDFPageInterpreter(resource_manager, converter)

        with open(path, 'rb') as fh:

            for page in PDFPage.get_pages(fh,
                                        caching=True,
                                        check_extractable=True):
                page_interpreter.process_page(page)

            text = fake_file_handle.getvalue()

        # close open handles
        converter.close()
        fake_file_handle.close()

        return text

    resumeTxt = []
    resumeDir=os.getcwd()+'\\uploads\\resume\\'
    for filename in os.listdir(resumeDir):
        if(filename.endswith(".pdf")):
            try:
                resumeTxt.append(convert_pdf_to_txt(resumeDir+filename))
                break
            except Exception:
                pass

    resumeTxtNoStopword = []

    for resume in resumeTxt:
        text = resume
        text = text.split()
        useful_words = [w for w in text ]#if w not in sw]
        resumeTxtNoStopword.append(" ".join(useful_words))

    def tokenize(text):
        # obtains tokens with a least 1 alphabet
        pattern = re.compile(r'[A-Za-z]+[\w^\']*|[\w^\']*[A-Za-z]+[\w^\']*')
        return pattern.findall(text.lower())

    i = 0
    tokenized_resumes = []
    for resume in resumeTxtNoStopword:
        r = tokenize(resume)
        tokenized_resumes.append(r)
        i += 1
    if(len(tokenized_resumes)!=0):
        pass
        #print(tokenized_resumes[0])


    ##################
    nlp = spacy.load('en_core_web_sm')
    #noun_chunks = nlp.noun_chunks

    def getSimilarSkills(tokens):
        model=gensim.models.Word2Vec.load(os.getcwd()+ "\\models\\model_skill_extraction")
        skill_dict={}
        for token in tokens:
            if(token in model.wv.key_to_index):
                skill_dict[token]=model.wv.similar_by_word(token,topn=5)
        print("\n\n======skill dict:\n\n",skill_dict)
        print("\n\n======skill dict:\n\n")
        return skill_dict


    def extract_skills(resume_text):
        #stopwords=set(STOPWORDS.words('english'))
        nlp_text = nlp(resume_text)

        # noun chunks are the noun phrases in the resume text
        noun_chunks = [chunk.text for chunk in nlp_text.noun_chunks]# if chunk.text not in stopwords]

        # removing stop words and implementing word tokenization
        tokens = [token.text for token in nlp_text if not token.is_stop]# and token.text not in stopwords]

        similarSkills=getSimilarSkills(tokens)

        global skillist
        global user_extracted_skills
        skills=skillist

        userskillset = []
        for token in tokens:
            for skill in skills:
                if token.lower() == skill.lower() and abs(len(token)-len(skill))<=5:
                    userskillset.append(token)

        # check for bi-grams and tri-grams (example: machine learning)
        for token in noun_chunks:
            token = token.lower()
            if token.lower() in  skills:# and abs(len(token)-len(skill))<=2:
                userskillset.append(token)

        #print("Skillset:\n", skillset)

        return [i.capitalize() for i in set([i.lower() for i in userskillset])]

    resumeText=''.join(ele+' ' for ele in tokenized_resumes[0])
    user_extracted_skills=extract_skills(resumeText)#''.join(tokenized_resumes[0])))#tokenized_resumes[0].toString()))
    print("===================\nUser Skills:\n")
    print(user_extracted_skills)
    #generateResult()

def generateResult():
    global skillist
    global skillListMap
    global user_extracted_skills
    global domainIndexArray
    global allResults

    uSkillArray=[0]*(len(skillListMap)-1)

    for uskill in user_extracted_skills:
        if skillListMap[uskill.lower()]<len(uSkillArray):
            uSkillArray[skillListMap[uskill.lower()]]=1

    #load pickle model
    print("============skillist length=",str(len(skillist))+"=============")
    print(skillist[:10])
    print("=======dir="+os.getcwd())
    model=pickle.load(open(os.getcwd()+"\\models\\nvBayes.pkl","rb"))
    y_pred=model.predict_proba([uSkillArray])
    print("y_pred= ",y_pred)

    y_pred_op=model.predict([uSkillArray])
    print(type(y_pred_op))
    print(domainIndexArray[y_pred_op[0]])

    #dictionay of predicted output
    domain_predicted_output={}
    for i in range(len(domainIndexArray)):
        domain_predicted_output[domainIndexArray[i]]=y_pred[0][i]
    #sort domain_predicted_output
    choseFiveDomainsfromResume=sorted(domain_predicted_output.items(),key=operator.itemgetter(1),reverse=True)[:5]
    print(choseFiveDomainsfromResume)

    requiredOtherSkills=pd.read_csv(os.getcwd()+"\\appMain\\otherksills.csv")
    requiredOtherSkills=requiredOtherSkills.values.tolist()
    print("requiredOtherSkills=\n",requiredOtherSkills)
    #dictionary of requiredOtherSkills
    '''requiredOtherSkillsDict={}
    for i in range(1,len(requiredOtherSkills)):
        for j in range(1,len(requiredOtherSkills[0])):
            #requiredOtherSkillsDict[requiredOtherSkills[0][i]][requiredOtherSkills[j][0]]=requiredOtherSkills[i][j]
            pass    '''
    
    print(requiredOtherSkills[1][1])
    print("==================")
    #print(requiredOtherSkillsDict)
    otherSkillOrder=[	'quant'	,'verbal',	'logical',	'communication'	,'DSA',	'OOPM',	'Web'	,'DBMS',	'CN']
    OtherSkillsDict={}
    for i in range(len(requiredOtherSkills)):
        OtherSkillsDict[requiredOtherSkills[i][0]]=requiredOtherSkills[i][1:]
    
    #drop first key from dict
    #OtherSkillsDict.pop('nan',None)

    print(OtherSkillsDict)

    '''userOtherSkillDict={}
    for i in range(len(choseFiveDomainsfromResume)):
        userOtherSkillDict[choseFiveDomainsfromResume[i]]=allResults[]'''
    print(allResults)
    userOtherSkills=[]
   
    thresholdMarks=2
    #threshold for individual domain


    userOtherSkills.append(1 if allResults['apti']['apti_tags']['Quantative Aptitude']> thresholdMarks else 0)
    userOtherSkills.append(1 if allResults['apti']['apti_tags']['Verbal Reasoning']> thresholdMarks else 0)
    userOtherSkills.append(1 if allResults['apti']['apti_tags']['Logical Reasoning']> thresholdMarks else 0)

    userOtherSkills.append(1 if allResults['soft']['soft_tags']['ss']> thresholdMarks else 0)

    #{'dbms': 0, 'dsa': 0, 'webd': 0, 'oops': 0, 'cn': 0}}
    userOtherSkills.append(1 if allResults['tech']['tech_tags']['dsa']> thresholdMarks else 0)
    userOtherSkills.append(1 if allResults['tech']['tech_tags']['oops']> thresholdMarks else 0)
    userOtherSkills.append(1 if allResults['tech']['tech_tags']['webd']> thresholdMarks else 0)
    userOtherSkills.append(1 if allResults['tech']['tech_tags']['dbms']> thresholdMarks else 0)
    userOtherSkills.append(1 if allResults['tech']['tech_tags']['cn']> thresholdMarks else 0)
    
    ##hamming distance
    maxthresholdHamming=4
    hammingArray=[]
    for i in range(len(choseFiveDomainsfromResume)):
        hammingArray.append(hamming(OtherSkillsDict[choseFiveDomainsfromResume[i][0]],userOtherSkills))
  
    

    '''for ele in choseFiveDomainsfromResume:
        bestMatch.append(ele[0])  '''
    print("allresult=========")
    print(allResults)
    print(OtherSkillsDict)

    finalThreeDomains=[]

    #66-33 split
    for i in range(len(choseFiveDomainsfromResume)):
        #choseFiveDomainsfromResume[i][1]=0.66*choseFiveDomainsfromResume[i][1]+0.33*(len(otherSkillOrder)-hammingArray[i])
        finalThreeDomains.append(Domain_Probability(choseFiveDomainsfromResume[i][0],
        0.66*choseFiveDomainsfromResume[i][1]+0.33*(len(otherSkillOrder)-hammingArray[i]
        )))
    #sort choseFiveDomainsfromResume
    #choseFiveDomainsfromResume=sorted(choseFiveDomainsfromResume,key=operator.itemgetter(1),reverse=True)[:3]
    #print(choseFiveDomainsfromResume)
    #sort finalThreeDomains
    finalThreeDomains=sorted(finalThreeDomains,key=lambda x:x.probability,reverse=True)[:3]
    print(finalThreeDomains)
    for ele in finalThreeDomains:
        print(ele.domain,ele.probability)
    
    #graph plot
    labels={}
    dataset={}
    topRequired=pd.read_csv(os.getcwd()+"\\appMain\\domain-wise-top-skill-requirements.csv")

    for i in range(len(finalThreeDomains)):
        nw=topRequired[finalThreeDomains[i].domain].to_list()
        ss=topRequired[finalThreeDomains[i].domain].to_list()
        for j in range(len(nw)):
            nw[j]=nw[j].strip('(').strip(')').strip("'").strip("'").split(',')[0]
            ss[j]=ss[j].strip('(').strip(')').strip("'").strip("'").split(',')[1]
        for j in range(len(nw)):
            nw[j]=nw[j].strip("'")
            ss[j]=ss[j].strip("'").strip()

        labels[finalThreeDomains[i].domain]=nw
        dataset[finalThreeDomains[i].domain]=ss
    
    print("laberl= \n",labels)
    print("data=\n",dataset)
    
    return finalThreeDomains,labels,dataset

def hamming(l1,l2):
    return sum(i==1 and j==0  for i, j in zip(l1, l2))

def plot():
    #read top skll requiremnets excel
    pass
    #print(topRequired)
