from transformers import pipeline
import torch

class BERTThreatClassifier:
    """
    Local BERT-based Classifier for semantic threat detection.
    Uses DistilBERT for low-latency CPU inference.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BERTThreatClassifier, cls).__new__(cls)
            # Load the classifier (Sentiment as proxy for maliciousness/negativity)
            # In a production banking environment, this would be a fine-tuned 
            # BERT model on prompt injection and banking fraud data.
            cls._instance.classifier = pipeline(
                "sentiment-analysis", 
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=-1 # Ensure CPU usage
            )
        return cls._instance

    def predict_safe_score(self, text):
        """
        Returns a 'Safe' probability score between 0.0 and 1.0.
        Low score indicates malicious or negative sentiment (threat).
        """
        try:
            # Truncate to BERT's 512 token limit
            result = self.classifier(text[:512])[0]
            label = result['label']
            score = result['score']
            
            # Repurpose SST-2 (Sentiment) for maliciousness proxy
            # POSITIVE sentiment -> 1.0 (Safe)
            # NEGATIVE sentiment -> 0.0 (Potentially Malicious)
            if label == "POSITIVE":
                return float(score)
            else:
                # Map negative sentiment to lower safety score
                return 1.0 - float(score)
        except Exception as e:
            print(f"BERT Inference Error: {e}")
            return 0.5 # Default to uncertain on error

# Singleton instance for high-performance reuse
bert_scorer = BERTThreatClassifier()

def get_bert_safety_score(text):
    return bert_scorer.predict_safe_score(text)
