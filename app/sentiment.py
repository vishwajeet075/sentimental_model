from transformers import pipeline
import torch

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = pipeline(
            task="sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",  # Replace with DistilBERT
            device=-1  # Force CPU (Render does not support GPU)
        )

    def analyze(self, text: str) -> dict:
        """
        Analyze the sentiment of given text
        Returns: dict with sentiment label and score
        """
        try:
            result = self.analyzer(text)[0]
            # Convert sentiment to numerical score for storing
            sentiment_map = {
                'POSITIVE': 1.0,
                'NEGATIVE': -1.0,
                'NEUTRAL': 0.0
            }
            return {
                'label': result['label'],
                'score': sentiment_map.get(result['label'], 0.0),
                'confidence': result['score']
            }
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return {'label': 'NEUTRAL', 'score': 0.0, 'confidence': 1.0}