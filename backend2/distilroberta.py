from transformers import pipeline
classifier = pipeline("sentiment-analysis", model="j-hartmann/emotion-english-distilroberta-base", top_k=1)

def analyze_sentiment(text):
    prediction = classifier(text)
    print(prediction[0][0]['label'])
    return prediction[0][0]['label']
