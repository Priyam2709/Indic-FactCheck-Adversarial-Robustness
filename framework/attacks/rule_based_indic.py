import random
from framework.attacks.base import BaseAttack
from indicnlp.tokenize import indic_tokenize

class HomoglyphPerturbation(BaseAttack):
    def __init__(self):
        super().__init__("Homoglyph Perturbation", "claim", "character")
        # Dummy indic homoglyph dictionary (e.g. replacing Hindi characters with similar looking ones if possible, or Latin homoglyphs)
        self.homoglyph_map = {
            'ा': 'ा', # Placeholder for actual homoglyphs
            'a': 'а',
            'e': 'е',
            'o': 'о'
        }
        
    def generate(self, text: str) -> str:
        res = list(text)
        for i in range(len(res)):
            if res[i] in self.homoglyph_map and random.random() < 0.3:
                res[i] = self.homoglyph_map[res[i]]
        return "".join(res)

class WordJumbling(BaseAttack):
    def __init__(self):
        super().__init__("Jumbling", "claim", "word")
        
    def generate(self, text: str) -> str:
        # Use indic tokenization for proper word boundary parsing
        words = indic_tokenize.trivial_tokenize(text)
        if len(words) < 3:
            return text
        
        # Swap two random adjacent words
        idx = random.randint(0, len(words) - 2)
        words[idx], words[idx+1] = words[idx+1], words[idx]
        
        # Basic re-join (Note: proper indic detokenization is more complex)
        return " ".join(words)
        
class RepeatPhrases(BaseAttack):
    def __init__(self):
        super().__init__("Repeat Phrases", "claim", "word")
        
    def generate(self, text: str) -> str:
        words = indic_tokenize.trivial_tokenize(text)
        if len(words) < 4:
            return text + " " + text
        
        phrase = " ".join(words[:len(words)//4])
        return text + " " + phrase
