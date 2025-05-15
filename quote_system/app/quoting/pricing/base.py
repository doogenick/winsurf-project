from abc import ABC, abstractmethod
from typing import Dict, Any

class PricingRule(ABC):
    """Base class for all pricing rules."""
    
    @abstractmethod
    def apply(self, data: Dict) -> float:
        """Apply the pricing rule to the given data."""
        pass

    @abstractmethod
    def validate(self, data: Dict) -> bool:
        """Validate if the rule can be applied to the given data."""
        pass

class PricingRuleRegistry:
    def __init__(self):
        self.rules = {}
        
    def register(self, rule_name: str, rule_class: type):
        """Register a new pricing rule."""
        if not issubclass(rule_class, PricingRule):
            raise ValueError("Rule must inherit from PricingRule")
        self.rules[rule_name] = rule_class
        
    def get_rule(self, rule_name: str) -> type:
        """Get a registered rule class."""
        return self.rules.get(rule_name)
        
    def apply_rules(self, data: Dict, rule_names: list) -> float:
        """Apply a sequence of rules to the data."""
        total = 0
        for rule_name in rule_names:
            rule = self.get_rule(rule_name)
            if rule and rule.validate(data):
                total += rule.apply(data)
        return total
