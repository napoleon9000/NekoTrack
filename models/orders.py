import datetime
from dataclasses import dataclass, field
import uuid
from enum import Enum
class PlushieType(Enum):
    small = 'small'   # 8 inch
    medium = 'medium'  # < 10 credits
    large = 'large'    # > 10 credits
    keychain = 'keychain'    # keychain or 4 inch
    figures = 'figures'    # shouban

class OrderStatus(Enum):
    ordered = 'ordered'   # ordered from original seller
    to_warehouse = 'to_warehouse'  # shipped from seller, on the way to China warehouse
    to_US = 'to_US'    # shipped from China warehouse, on the way to US
    delivered = 'delivered'   # delivered to store
    cancelled = 'cancelled'   # cancelled 

@dataclass
class Order:
    image_path: str = None
    name: str = None
    seller: str = None 
    status: OrderStatus = None
    tracking_number: str = None
    amount: int = None
    plushie_type: PlushieType = None
    price: float = None
    shipping_cost: float = None
    shipping_date: datetime.datetime = None
    expected_deliver_date: datetime.datetime = None
    notes: str = None
    created_date: datetime.datetime = field(default_factory=datetime.datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Inventory(Order):
    location: str = None
    
