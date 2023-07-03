#!/usr/bin/env python
# coding: utf-8

# Import necessary libraries
import numpy as np
import pandas as pd
import csv
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import classification_report, confusion_matrix
from wordcloud import WordCloud, STOPWORDS,ImageColorGenerator
from sklearn.feature_extraction.text import TfidfVectorizer
import  numpy as np
import requests
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, f1_score
from sklearn import metrics
from sklearn.metrics import roc_auc_score
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set plotting styles
sns.set_style("darkgrid")
sns.set_context("poster")
plt.rcParams["figure.figsize"] = [8, 6]


# Read the data from CSV file
data = pd.read_csv("Allnoted_Nan_class.csv")

# Remove unwanted projects from the data
data = data[data['teamtat_project'] != 'project_8']
data = data[data['teamtat_project'] != 'project_7']
data = data[data['teamtat_project'] != 'project_6']

# Lowercase all words in the 'note_text' column
data['note_text'] = data['note_text'].str.lower()

# Remove punctuation from the 'note_text' column
data['note_text'] = data['note_text'].apply(lambda x: ' '.join([word for word in x.split() if word.isalnum()]))

# Remove numerical values from the 'note_text' column
data['note_text'] = data['note_text'].apply(lambda x: ' '.join([word for word in x.split() if not word.isdigit()]))

# Remove stopwords from the 'note_text' column
stop_words = stopwords.words('english')
data['note_text'] = data['note_text'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop_words)]))

# Lemmatize the words in the 'note_text' column
w_tokenizer = nltk.tokenize.WhitespaceTokenizer()
lemmatizer = nltk.stem.WordNetLemmatizer()

def lemmatize_text(text):
    return ' '.join([lemmatizer.lemmatize(w) for w in w_tokenizer.tokenize(text)])

data['text_lemmatized'] = data.note_text.apply(lemmatize_text)

# Replace class labels with appropriate values
data['Class'] = data['Class'].replace({'EXPRESS/PUMP': 'BREAST', 'MIXED': 'BOTTLE', 'nan-feeding-related': 'NA', 'nan-related': 'NA', 'nan-not-related': 'NA'})

# Plot the distribution of class labels
print(data["Class"].value_counts())
data.groupby('Class').size().plot(kind='pie', y="Class", autopct='%1.1f%%')

# Split the data into train and test sets
BREAST = data[data["Class"] == "BREAST"]
BOTTLE = data[data["Class"] == "BOTTLE"]
NA = data[data["Class"] == "NA"]

downsample_breast = resample(BREAST, replace=True, n_samples=len(BOTTLE), random_state=42)
downsample_NA = resample(NA, replace=True, n_samples=len(BOTTLE), random_state=42)

data_downsampled = pd.concat([downsample_breast, BOTTLE, downsample_NA])

# Print the distribution of class labels after downsampling
print(data_downsampled["Class"].value_counts())
data_downsampled.groupby('Class').size().plot(kind='pie', y="class", label="Type", autopct='%1.1f%%')

# Prepare the data for training and testing
Notes = np.array(data_downsampled['text_lemmatized'])
classs = np.array(data_downsampled['Class'])

x_train, x_test, y_train, y_test = train_test_split(Notes, classs, test_size=0.3, random_state=12)

tf_vectorizer = TfidfVectorizer()
x_train_tfidf = tf_vectorizer.fit_transform(x_train)
x_test_tfidf = tf_vectorizer.transform(x_test)

import xgboost as xgb
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import LabelEncoder

# Convert class labels to numeric values
label_encoder = LabelEncoder()
y_train_encoded = label_encoder.fit_transform(y_train)
y_test_encoded = label_encoder.transform(y_test)

# Create DMatrix for XGBoost
dtrain = xgb.DMatrix(x_train_tfidf, label=y_train_encoded)
dtest = xgb.DMatrix(x_test_tfidf)

# Set XGBoost parameters
params = {
    'objective': 'multi:softmax',
    'num_class': len(label_encoder.classes_),
    'seed': 12
}

# Define the parameter grid for hyperparameter tuning
param_grid = {
    'max_depth': [3, 6, 9],
    'learning_rate': [0.1, 0.01, 0.001],
    'gamma': [0, 0.1, 0.2]
}

# Create XGBoost classifier
xgb_classifier = xgb.XGBClassifier(**params)

# Perform grid search with cross-validation
grid_search = GridSearchCV(estimator=xgb_classifier, param_grid=param_grid, cv=5)
grid_search.fit(x_train_tfidf, y_train_encoded)

# Get the best model and its hyperparameters
best_model = grid_search.best_estimator_
best_params = grid_search.best_params_

# Make predictions on the test data using the best model
y_pred_encoded = best_model.predict(x_test_tfidf)
y_pred = label_encoder.inverse_transform(y_pred_encoded)

# Calculate accuracy on the test data
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred,average = 'macro')
recall = recall_score(y_test, y_pred,average = 'macro')
f1 = f1_score(y_test, y_pred,average = 'macro')


print("Accuracy:", accuracy)
print("precision:", precision)
print("recall:", recall)
print("f1:", f1)
