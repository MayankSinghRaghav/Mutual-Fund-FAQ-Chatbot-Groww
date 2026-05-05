import re

class SafetyFilter:
    def is_safe(self, query):
        # Refuse advisory or PII requests
        advisory_keywords = [
            "should i invest", "which fund is better", "give me advice",
            "predict", "future returns", "best fund", "buy or sell"
        ]
        pii_patterns = [
            r"\b\d{10}\b", # Phone
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", # Email
            r"\b[A-Z]{5}\d{4}[A-Z]\b" # PAN
        ]
        
        query_lower = query.lower()
        if any(k in query_lower for k in advisory_keywords):
            return False, "I can only provide factual information about HDFC Mutual Fund schemes. I cannot provide investment advice or recommendations."
            
        if any(re.search(p, query) for p in pii_patterns):
            return False, "For your security, please do not share personal information (Phone, Email, or PAN)."
            
        return True, None
