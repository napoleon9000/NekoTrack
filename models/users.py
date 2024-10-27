from dataclasses import dataclass, asdict
from typing import List

@dataclass
class Redemption:
    item: str
    date: str
    credits: int


@dataclass
class User:
    uuid: str
    phone_number: str
    registration_date: str
    credits: int = 0
    tokens: int = 0
    name: str = ""
    notes: str = ""
    redemption_history: List[Redemption] = None
    
    def __post_init__(self):
        if self.redemption_history is None:
            self.redemption_history = []

    def to_dict(self):
        return asdict(self)
