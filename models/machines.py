from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import uuid

@dataclass
class Record:
    machine_id: str
    coins_in: int
    toys_payout: int
    param_strong_strength: float
    param_medium_strength: float
    param_weak_strength: float
    param_award_interval: int
    param_mode: str = ''
    notes: Optional[str] = None
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Machine:
    name: str
    location: str
    status: str
    param_strong_strength: float
    param_medium_strength: float
    param_weak_strength: float
    param_award_interval: int
    param_mode: str = ''
    id: str = None
    notes: Optional[str] = None
    image: Optional[str] = None   # path to image

    def get_params(self):
        """Summary of the machine parameters"""
        try:
            results = f'{self.param_strong_strength}, {self.param_medium_strength}, {self.param_weak_strength} | {self.param_award_interval}, {self.param_mode}'
            return results
        except Exception as e:
            return None