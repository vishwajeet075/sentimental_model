from transformers import pipeline
import torch

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = pipeline(
            task="sentiment-analysis",
            model="finiteautomata/bertweet-base-sentiment-analysis",
            device=0 if torch.cuda.is_available() else -1
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
                'POS': 1.0,
                'NEU': 0.0,
                'NEG': -1.0
            }
            return {
                'label': result['label'],
                'score': sentiment_map.get(result['label'], 0.0),
                'confidence': result['score']
            }
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return {'label': 'NEU', 'score': 0.0, 'confidence': 1.0}