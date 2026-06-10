from crewai import Task

from .agent import inventory_agent

from shared.models import (
    InventoryAgentOutput
)


inventory_task = Task(

    description="""

    Step 1:
    Fetch today's inventory data.

    Step 2:
    Store today's inventory data in MongoDB.

    Step 3:
    Retrieve historical sales records.

    Step 4:
    Analyze:

    - sales patterns
    - demand trends
    - seasonal effects
    - stock depletion risks

    Step 5:
    Determine products that require replenishment.

    Step 6:
    Estimate required quantity.

    Return ONLY valid JSON.

    Format:

    {
      "products": [
        {
          "product_id": "",
          "product_name": "",
          "quantity": 0,
          "category": ""
        }
      ]
    }

    """,

    expected_output="JSON matching InventoryAgentOutput",
    output_pydantic=InventoryAgentOutput,

    agent=inventory_agent
)
