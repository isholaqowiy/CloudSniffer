import math
import re
from typing import Dict, Any

class StatisticalAnalyzer:
    @staticmethod
    def calculate_metrics(text: str) -> Dict[str, Any]:
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        words = [w.lower() for w in re.findall(r'\b\w+\b', text)]
        
        if not sentences or not words:
            return {"perplexity_score": 50.0, "burstiness_score": 0.0, "sentence_variance": 0.0, "repetition_index": 1.0}
            
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths)
        
        # Sentence Variance Calculation
        variance_sum = sum((l - avg_sentence_length) ** 2 for l in sentence_lengths)
        sentence_variance = variance_sum / len(sentence_lengths)
        
        # Burstiness (Standard Deviation of sentence length structural distributions)
        burstiness_score = math.sqrt(sentence_variance)
        
        # Unique Word Type-Token Ratio (Repetition Index)
        unique_words = set(words)
        repetition_index = len(unique_words) / len(words) if words else 1.0
        
        # Simulating analytical heuristic scaling bounds 
        # Lower burstiness and lower structural variances correlate closely with predictable distributions
        base_perplexity = 100.0 - (repetition_index * 40.0)
        if burstiness_score < 3.0:
            base_perplexity -= 25.0
            
        return {
            "perplexity_score": max(min(base_perplexity, 100.0), 10.0),
            "burstiness_score": round(burstiness_score, 2),
            "sentence_variance": round(sentence_variance, 2),
            "repetition_index": round(repetition_index, 2)
        }
