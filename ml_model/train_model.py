import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.metrics import accuracy_score
import pickle
import os

# 1. Load both datasets
df_fake = pd.read_csv('../data/Fake.csv')
df_true = pd.read_csv('../data/True.csv')

# 2. Add labels
df_fake['label'] = 'FAKE'
df_true['label'] = 'REAL'

# 3. Combine both
df = pd.concat([df_fake, df_true], axis=0).reset_index(drop=True)

# 4. Clean + Combine title + text
df['title'] = df['title'].fillna('')
df['text'] = df['text'].fillna('')
df['content'] = df['title'] + " " + df['text']
df = df[['content', 'label']].dropna()

# 5. TF-IDF Vectorization
vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)
X = vectorizer.fit_transform(df['content'])
y = df['label']

# 6. Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 7. Train model
model = PassiveAggressiveClassifier(max_iter=1000)
model.fit(X_train, y_train)

# 8. Evaluate
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Model trained. Accuracy: {acc:.2f}")

# 9. Save model and vectorizer
# No need to make any new directory — already in ml_model/
pickle.dump(model, open('model.pkl', 'wb'))
pickle.dump(vectorizer, open('tfidf.pkl', 'wb'))


print("✅ Model and vectorizer saved successfully.")
