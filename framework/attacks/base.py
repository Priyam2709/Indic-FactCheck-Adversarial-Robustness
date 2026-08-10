from abc import ABC, abstractmethod

class BaseAttack(ABC):
    """
    Abstract base class for all Adversarial Attacks against Fact-Checking models.
    """
    
    def __init__(self, attack_name: str, target: str, level: str):
        self.attack_name = attack_name
        self.target = target  # e.g., "claim", "evidence", "pair"
        self.level = level    # e.g., "character", "word", "sentence"
        
    @abstractmethod
    def generate(self, text: str) -> str:
        """
        Applies the adversarial perturbation to the given text.
        Returns the modified text.
        """
        pass
