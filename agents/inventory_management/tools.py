import requests

from typing import Any

from crewai.tools import BaseTool
from pydantic import BaseModel, Field, model_validator

from shared.database import sales_collection


class EmptyToolInput(BaseModel):
    pass


class StoreInventoryInput(BaseModel):
    inventory_data: Any = Field(
        ...,
        description="Inventory snapshot or list of inventory snapshots to store",
    )

    @model_validator(mode='before')
    @classmethod
    def handle_properties_wrap(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "properties" in data and len(data) == 1:
                return data["properties"]
            if "properties" in data and isinstance(data["properties"], dict) and "inventory_data" in data["properties"]:
                return data["properties"]
        return data


class InventoryAPITool(BaseTool):

    name: str = "inventory_api"

    description: str = (
        "Fetch today's inventory sales data"
    )
    args_schema: type[BaseModel] = EmptyToolInput

    def _run(self, **kwargs):

        response = requests.get(
            "http://127.0.0.1:5000/inventory"
        )

        response.raise_for_status()

        raw = response.json()

        # Return compact summary to reduce LLM token usage
        compact = [
            {
                "id": p["product_id"],
                "name": p["product_name"],
                "category": p["category"],
                "sales": p["today_sales"],
                "stock": p["remaining_stock"],
            }
            for p in raw
        ]

        # Store the full raw data internally for MongoDB
        self._raw_data = raw

        return compact


class StoreInventoryTool(BaseTool):

    name: str = "store_inventory"

    description: str = (
        "Store inventory snapshots in MongoDB. Pass the full list from inventory_api."
    )
    args_schema: type[BaseModel] = StoreInventoryInput

    def _run(self, inventory_data):

        if isinstance(inventory_data, dict):
            inventory_data = [inventory_data]

        # Strip any non-serializable fields before insert
        docs = []
        for item in inventory_data:
            doc = {k: v for k, v in item.items() if k != "_id"}
            docs.append(doc)

        sales_collection.insert_many(docs)

        # Return a short confirmation — do NOT echo back all the data
        return f"Stored {len(docs)} inventory records successfully."


class HistoricalSalesTool(BaseTool):

    name: str = "historical_sales"

    description: str = (
        "Retrieve historical sales data"
    )
    args_schema: type[BaseModel] = EmptyToolInput

    def _run(self, **kwargs):

        raw = list(
            sales_collection.find(
                {},
                {"_id": 0}
            ).sort("_id", -1).limit(5)  # Only 5 records to stay under TPM
        )

        # Return compact form to save tokens
        compact = []
        for p in raw:
            compact.append({
                "id": p.get("product_id", p.get("id", "")),
                "name": p.get("product_name", p.get("name", "")),
                "sales": p.get("today_sales", p.get("sales", 0)),
                "stock": p.get("remaining_stock", p.get("stock", 0)),
                "date": p.get("date", ""),
            })

        return compact
