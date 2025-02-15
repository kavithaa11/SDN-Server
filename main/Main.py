
from tkinter import messagebox
from tkinter import *
from tkinter import simpledialog
import tkinter
import matplotlib.pyplot as plt
import numpy as np
from tkinter import simpledialog
from tkinter import filedialog
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
import seaborn as sns
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn import svm
from sklearn.ensemble import VotingClassifier
import pickle

main = tkinter.Tk()
main.title("Classification of Software Defined Network Traffic to Provide Quality of Service") #designing main screen
main.geometry("1300x1200")

global filename, dataset
global X, Y
global X_train, X_test, y_train, y_test
global accuracy, precision, recall, fscore, labels, nin_model, vc
global scaler, labels, label_encoder

def uploadDataset():
    global filename, dataset, labels
    filename = filedialog.askopenfilename(initialdir="Dataset")
    text.delete('1.0', END)
    text.insert(END,filename+" loaded\n\n")
    dataset = pd.read_csv(filename)
    text.insert(END,str(dataset))
    labels, label_count = np.unique(dataset['Label'], return_counts=True)
    label = dataset.groupby('Label').size()
    label.plot(kind="bar")
    plt.xlabel("Network Category Type")
    plt.ylabel("Count")
    plt.title("Network Category Graph")
    plt.show()

def DatasetPreprocessing():
    text.delete('1.0', END)
    global X, Y, dataset, label_encoder, scaler
    #dataset contains non-numeric values but ML algorithms accept only numeric values so by applying Lable
    #encoding class converting all non-numeric data into numeric data
    dataset.fillna(0, inplace = True)
    dataset.drop(['Traffic_Type'], axis = 1,inplace=True)
    label_encoder = []
    columns = dataset.columns
    types = dataset.dtypes.values
    for i in range(len(types)):
        name = types[i]
        if name == 'object': #finding column with object type
            le = LabelEncoder()
            dataset[columns[i]] = pd.Series(le.fit_transform(dataset[columns[i]].astype(str)))#encode all str columns to numeric 
            label_encoder.append(le)    
    text.insert(END,"Dataset Normalization & Preprocessing Task Completed\n\n")
    text.insert(END,str(dataset)+"\n\n")
    #dataset preprocessing such as replacing missing values, normalization and splitting dataset into train and test
    data = dataset.values
    X = data[:,0:data.shape[1]-1] #extracting X and Y Features from the dataset
    Y = data[:,data.shape[1]-1]
    print(X.shape)
    print(np.unique(Y))
    print(Y)
    Y = Y.astype(int)
    indices = np.arange(X.shape[0])
    np.random.shuffle(indices) #shuffling the dataset
    X = X[indices]
    Y = Y[indices]
    #normalizing or scaling values
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    

def splitDataset():
    text.delete('1.0', END)
    global X_train, X_test, y_train, y_test, scaler, X, Y
    #splitting dataset into train and test where application using 80% dataset for training and 20% for testing
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2) #split dataset into train and test
    text.insert(END,"Dataset Train & Test Splits\n")
    text.insert(END,"Total records found in dataset : "+str(X.shape[0])+"\n")
    text.insert(END,"80% dataset used for training  : "+str(X_train.shape[0])+"\n")
    text.insert(END,"20% dataset user for testing   : "+str(X_test.shape[0])+"\n")
    X = X[0:10000]
    Y = Y[0:10000]
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2) #split dataset into train and test
    X_train, X_test1, y_train, y_test1 = train_test_split(X, Y, test_size=0.1) #split dataset into train and test


def calculateMetrics(algorithm, testY, predict):
    global labels
    p = precision_score(testY, predict,average='macro') * 100
    r = recall_score(testY, predict,average='macro') * 100
    f = f1_score(testY, predict,average='macro') * 100
    a = accuracy_score(testY,predict)*100
    accuracy.append(a)
    precision.append(p)
    recall.append(r)
    fscore.append(f)
    text.insert(END,algorithm+" Accuracy  : "+str(a)+"\n")
    text.insert(END,algorithm+" Precision : "+str(p)+"\n")
    text.insert(END,algorithm+" Recall    : "+str(r)+"\n")
    text.insert(END,algorithm+" FSCORE    : "+str(f)+"\n\n")
    conf_matrix = confusion_matrix(testY, predict)
    ax = sns.heatmap(conf_matrix, xticklabels = labels, yticklabels = labels, annot = True, cmap="viridis" ,fmt ="g");
    ax.set_ylim([0,len(labels)])
    plt.title(algorithm+" Confusion matrix") 
    plt.ylabel('True class') 
    plt.xlabel('Predicted class') 
    plt.show() 

#now train Ensemble algorithm    
def runEnsemble():
    text.delete('1.0', END)
    global accuracy, precision, recall, fscore, vc
    global X_train, y_train, X_test, y_test
    accuracy = []
    precision = []
    recall = [] 
    fscore = []
    
    #creating random Forest Object
    rf = RandomForestClassifier()
    #creating J48 Decision Tree object
    dt = DecisionTreeClassifier()
    #creating SVM object
    svm_cls = svm.SVC()
    #now grouping all classififers into one as ensemble
    vc = VotingClassifier(estimators=[('rf', rf), ('dt', dt), ('svm', svm_cls)], voting='hard')
    #now train ensemble on training data
    vc.fit(X_train, y_train)
    predict = vc.predict(X_test)
    calculateMetrics("Ensemble Random Forest, J48 & SVM", y_test, predict)

def graph():
    df = pd.DataFrame([['Ensemble Algorithm','Accuracy',accuracy[0]],['Ensemble Algorithm','Precision',precision[0]],['Ensemble Algorithm','Recall',recall[0]],['Ensemble Algorithm','FSCORE',fscore[0]],
                      ],columns=['Algorithms','Accuracy','Value'])
    df.pivot("Algorithms", "Accuracy", "Value").plot(kind='bar')
    plt.title("All Algorithm Comparison Graph")
    plt.show()    

def predict():
    global vc, scaler, label_encoder, labels
    text.delete('1.0', END)
    filename = filedialog.askopenfilename(initialdir="Dataset")#upload test data
    dataset = pd.read_csv(filename)#read data from uploaded file
    dataset.fillna(0, inplace = True)#removing missing values
    index = 0
    columns = dataset.columns
    types = dataset.dtypes.values
    for i in range(len(types)): #label encoding to convert non-numeric data to numeric data
        name = types[i]
        if name == 'object': #finding column with object type
            dataset[columns[i]] = pd.Series(label_encoder[index].fit_transform(dataset[columns[i]].astype(str)))
            index = index + 1
    dataset = dataset.values
    X = scaler.transform(dataset)#normalizing values
    traffic_type_predict = vc.predict(X)#performing prediction on test data
    for i in range(len(X)):
        text.insert(END,"Traffic Test Data : "+str(dataset[i]))
        text.insert(END,"Network Traffic Classified As ===> "+labels[int(traffic_type_predict[i])])
        text.insert(END,"\n")
    
    


font = ('times', 16, 'bold')
title = Label(main, text='Classification of Software Defined Network Traffic to Provide Quality of Service')
title.config(bg='LightGoldenrod1', fg='medium orchid')  
title.config(font=font)           
title.config(height=3, width=120)       
title.place(x=0,y=5)

font1 = ('times', 12, 'bold')
text=Text(main,height=22,width=140)
scroll=Scrollbar(text)
text.configure(yscrollcommand=scroll.set)
text.place(x=10,y=200)
text.config(font=font1)


font1 = ('times', 12, 'bold')
uploadButton = Button(main, text="Upload Network Traffic Dataset", command=uploadDataset)
uploadButton.place(x=50,y=100)
uploadButton.config(font=font1)  

preButton = Button(main, text="Dataset Preprocessing", command=DatasetPreprocessing)
preButton.place(x=370,y=100)
preButton.config(font=font1) 

nbButton = Button(main, text="Split Train-Test Data", command=splitDataset)
nbButton.place(x=610,y=100)
nbButton.config(font=font1) 

rfButton = Button(main, text="Run Ensemble Algorithm", command=runEnsemble)
rfButton.place(x=860,y=100)
rfButton.config(font=font1) 

graphButton = Button(main, text="Comparison Graph", command=graph)
graphButton.place(x=50,y=150)
graphButton.config(font=font1)

predictButton = Button(main, text="Traffic Classification from Test Data", command=predict)
predictButton.place(x=370,y=150)
predictButton.config(font=font1)  

#main.config(bg='OliveDrab2')
main.mainloop()
