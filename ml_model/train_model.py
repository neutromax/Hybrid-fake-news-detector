import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.metrics import accuracy_score
import pickle
import os

# === Load datasets ===
df_fake = pd.read_csv('../data/Fake.csv')
df_true = pd.read_csv('../data/True.csv')


# === Add labels ===
df_fake['label'] = 'FAKE'
df_true['label'] = 'REAL'

# === Keep only the headline/title column ===
df_fake['title'] = df_fake['title'].fillna('')
df_true['title'] = df_true['title'].fillna('')

# === Combine ===
df = pd.concat([df_fake[['title', 'label']], df_true[['title', 'label']]], axis=0).reset_index(drop=True)
df = df.rename(columns={"title": "content"})  # for consistency

# === Vectorize using TF-IDF ===
vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)
X = vectorizer.fit_transform(df['content'])
y = df['label']

# === Split ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === Train model ===
model = PassiveAggressiveClassifier(max_iter=1000)
model.fit(X_train, y_train)

# === Evaluate ===
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Model trained on HEADLINES. Accuracy: {accuracy:.2f}")

# === Save model and vectorizer to `ml_model/` folder ===
os.makedirs("ml_model", exist_ok=True)
pickle.dump(model, open("ml_model/model.pkl", "wb"))
pickle.dump(vectorizer, open("ml_model/tfidf.pkl", "wb"))

print("✅ Model and vectorizer saved to ml_model/ folder.")
