from pydantic import BaseModel
from typing import List


class ProductRecommendation(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    category: str



class InventoryAgentOutput(BaseModel):
    products: List[ProductRecommendation]
