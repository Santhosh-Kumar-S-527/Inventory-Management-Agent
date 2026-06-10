import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from crewai import Crew

from agents.inventory_management.agent import (
    inventory_agent
)

from agents.inventory_management.task import (
    inventory_task
)
from shared.database import sales_collection

print(
    "Records:",
    sales_collection.count_documents({})
)
crew = Crew(
    agents=[inventory_agent],
    tasks=[inventory_task],
    verbose=True
)

result = crew.kickoff()

print(result)
