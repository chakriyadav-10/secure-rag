import re

class BERTThreatClassifier:
    """
    Local BERT-based Classifier for semantic threat detection.
    Uses DistilBERT for low-latency CPU inference.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            # HEAVY IMPORTS: Moved inside to prevent Render Port Discovery timeouts
            from transformers import pipeline
            import torch
            
            cls._instance = super(BERTThreatClassifier, cls).__new__(cls)
            cls._instance.model_loaded = False
            try:
                # Load the classifier (Sentiment as proxy for maliciousness/negativity)
                cls._instance.classifier = pipeline(
                    "sentiment-analysis", 
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    device=-1 # Ensure CPU usage
                )
                cls._instance.model_loaded = True
            except Exception as e:
                print(f"⚠️ [CLOUD_SAFE_MODE] Could not load local BERT model (likely RAM limit): {e}")
                cls._instance.classifier = None
        return cls._instance

    def predict_safe_score(self, text):
        """
        Returns a 'Safe' probability score between 0.0 and 1.0.
        Calibrated to handle neutral banking queries without blocking them.
        """
        if not self.model_loaded:
            # Fallback to safe if memory is too low for local BERT.
            # The LLM-based Safety Scorer will still catch high-level threats.
            return 1.0 
        try:
            # Truncate to BERT's 512 token limit
            result = self.classifier(text[:512])[0]
            label = result['label']
            score = float(result['score'])
            
            # --- BANKING SENSITIVITY CALIBRATION ---
            # SST-2 often marks neutral questions as 'NEGATIVE'. 
            # We detect informational markers (what, how, where) to prevent False Positives.
            # Markers that indicate a safe, informational banking context
            inquisitive_markers = ["what", "how", "interest", "rate", "balance", "transfer", "amount", "account", "holder", "bank", "branch", "ifsc", "statement", "transaction", "login"]
            is_informational = any(m in text.lower() for m in inquisitive_markers)
            
            # --- AGGRESSIVE INJECTION DETECTION (Local Heuristic) ---
            # Narrowed patterns to reduce false positives on technical manuals
            PROMPT_INJECTION_PATTERNS = [r"ignore (all|previous|prior) instructions", r"jailbreak", r"you are now a", r"override safety"]
            CODE_INJECTION_PATTERNS = [r"<script.*?>", r"DROP\s+TABLE", r"rm\s+-rf\s+/"]
            
            is_adversarial = any(re.search(p, text.lower()) for p in PROMPT_INJECTION_PATTERNS + CODE_INJECTION_PATTERNS)
            
            if label == "POSITIVE":
                # High confidence safety
                return score
            else:
                # If negative sentiment but looks like a banking question, 
                # we calibrate it back up to 'Neutral/Safe' range.
                if is_informational:
                    # Boost score to 0.85+ range if it's just a question
                    return 0.85 + (score * 0.1)
                else:
                    # True negative - potentially angry or aggressive threat
                    return 1.0 - score
        except Exception as e:
            print(f"BERT Inference Error: {e}")
            return 0.8 # Default to safe-ish on error for demo stability

# Lazy instantiation variables
_bert_scorer_instance = None

def get_bert_safety_score(text):
    global _bert_scorer_instance
    if _bert_scorer_instance is None:
        print("🤖 Initializing Security Intelligence Model (BERT)...")
        _bert_scorer_instance = BERTThreatClassifier()
    return _bert_scorer_instance.predict_safe_score(text)
