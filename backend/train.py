import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

TRAINING_DATA = [
    ("Hey, are you free for lunch tomorrow?", "normal"),
    ("Sounds good, see you at 2pm.", "normal"),
    ("Please review the meeting notes when you have a moment.", "normal"),
    ("Can you share the report presentation slides?", "normal"),
    ("Happy birthday! Wishing you a fantastic year ahead.", "normal"),
    ("Thanks for your help with the project earlier.", "normal"),
    ("Let me know if the package arrived safely.", "normal"),
    ("Let's reschedule our sync call for Thursday.", "normal"),
    ("Hey baby, I miss you so much. Can you send gift cards urgently?", "malicious"),
    ("Hello dear, keep this a secret between us and wire the funds now.", "malicious"),
    ("Urgent: your account is compromised. Click this link immediately to verify.", "malicious"),
    ("Only you can help me my love, hurry and don't tell anyone about this.", "malicious"),
    ("Hey sweetie, trust me and invest in this private link right now.", "malicious"),
    ("Urgent action required! Hurry and send the verification code now.", "malicious"),
    ("My dear friend, this is a secret opportunity just for you, act asap.", "malicious"),
    ("Hey handsome, let's talk privately on this secret channel.", "malicious"),
]

def train_and_save(output_path: str = None):
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "honeytrap_detector.joblib")

    texts, labels = zip(*TRAINING_DATA)

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
        ("clf", LogisticRegression(random_state=42)),
    ])

    pipeline.fit(texts, labels)

    joblib.dump(pipeline, output_path)
    print(f"Model successfully trained and saved to {output_path}")
    return pipeline

if __name__ == "__main__":
    train_and_save()
