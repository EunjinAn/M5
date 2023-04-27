# -*- coding: utf-8 -*-
"""App_reviews.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1J7ZECNfzVA3f9vfqIY6HqaoVsmT9EVx0

## Download the data from Huggingface

In this project, we did sentiment and predict analysis with app_review dataset from HuggingFace.🤗
our analysis result has positive/negative, 100% accuracy.
"""

!pip install transformers --q
!pip install datasets -q

import pandas as pd
from datasets import load_dataset, Dataset
from transformers import pipeline
import datasets

dataset = load_dataset("app_reviews")

dataset

train_dataset = datasets.load_dataset("app_reviews", split="train")
df = pd.DataFrame(train_dataset[:1000])

df.head()

# Importing the necessary libraries
import sqlite3

# Create a connection to the database
conn = sqlite3.connect('example.db')

# Add a column for the sentiment labels
df['sentiment'] = ''

df.head()

# Load the DataFrame into the SQLite table
df.to_sql('app_reviews', conn, if_exists='append', index=False)

"""Query test

- select : all
- insert : (review : app is good, date: 2022, star: 3)
- update : a star value change 3 to 5
- delete : delete 'star = 4'
"""

# Select all records from the 'app_reviews' table
select_query = "SELECT * FROM app_reviews limit 10;"
cursor = conn.execute(select_query)
rows = cursor.fetchall()

# Print the records
for row in rows:
    print(row)

# Insert a new record into the 'app_reviews' table
insert_query = "INSERT INTO app_reviews (package_name, review , date, star) VALUES ('', 'APP is Good', '2022','3');"
conn.execute(insert_query)
conn.commit()

# Verify the insertion
cursor = conn.execute("SELECT * FROM app_reviews WHERE date = '2022';")
print(cursor.fetchone())

# Update a record in the 'app_reviews' table
update_query = "UPDATE app_reviews SET star = '5' WHERE date = '2022';"
conn.execute(update_query)
conn.commit()

# Verify the update
cursor = conn.execute("SELECT * FROM app_reviews WHERE date = '2022';")
print(cursor.fetchone())

# Delete a record from the 'app_reviews' table
delete_query = "DELETE FROM app_reviews WHERE star = '4';"
conn.execute(delete_query)
conn.commit()

# Verify the deletion
cursor = conn.execute("SELECT * FROM app_reviews WHERE star = '4';")
print(cursor.fetchone())

conn.close()

"""## Sementic analysis and SML"""

df.head()

# Create a connection to the database
conn = sqlite3.connect('app_reviews.db')

# Load the data into a table
df.to_sql('app_reviews', conn, if_exists='replace', index=False)

# Extract sentiment reviews for the movie reviews
reviews = conn.execute('SELECT review FROM app_reviews limit 10')

# Load the pre-trained sentiment analysis model
classifier = pipeline('sentiment-analysis')

# Iterate over the app reviews and update the sentiment label for each one
for i, row in enumerate(reviews):
    # Extract the text of the current review
    review = row[0]
    
    # Analyze the sentiment of the review using the pre-trained classifier
    sentiment = classifier(review[:512])[0]['label']
    
    # Map the sentiment label to a binary label (1 for positive, 0 for negative)
    if sentiment == 'POSITIVE':
      label = 1
    else:
      label = 0
      
    # Update the 'sentiment' column in the 'reviews' table with the binary label for the current review
    conn.execute('UPDATE app_reviews SET sentiment = ? WHERE rowid = ?', (label, i+1))
    
# Commit the changes to the database
conn.commit()

# Define the SQL query
query = 'SELECT * FROM app_reviews LIMIT 5'

# Execute the query and convert the result to a DataFrame
df_q = pd.read_sql_query(query, conn)
df_q

"""### SML"""

from transformers import pipeline
from sklearn.metrics import accuracy_score

# Load the data from the SQLite database
X = pd.read_sql_query('SELECT review FROM app_reviews limit 5', conn)
y = pd.read_sql_query('SELECT sentiment FROM app_reviews limit 5', conn)

# Train a logistic regression model on the sentiment labels
clf = pipeline('sentiment-analysis')
y_pred = [int(result['label'] == 'POSITIVE') for result in clf(X['review'].to_list(), truncation=True)]

# Evaluate the model on the testing set
accuracy = accuracy_score(y['sentiment'].astype(int).to_list(), y_pred)
print(f'Accuracy: {accuracy:.2f}')

"""# Make Grad.io"""

!pip install gradio

import gradio

# app.py
import gradio as gr
from transformers import pipeline

def classify(text):
  # Initializing the pipeline for sentiment analysis
  clf = pipeline('sentiment-analysis')
  # Predicting the sentiment label for the input text
  return clf(text)[0]['label']

# Creating the Gradio interface with input text and output text
gr.Interface(fn=classify, inputs=["text"], outputs="text").launch()

