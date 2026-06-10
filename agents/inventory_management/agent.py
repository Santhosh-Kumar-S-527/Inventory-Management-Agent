from crewai import Agent
from crewai import LLM

from .tools import (
    InventoryAPITool,
    StoreInventoryTool,
    HistoricalSalesTool
)


import time

class GroqLLM(LLM):
    def supports_function_calling(self):
        return False

    def _prepare_completion_params(self, messages, tools=None):
        params = super()._prepare_completion_params(messages, tools)
        for message in params.get("messages", []):
            message.pop("cache_breakpoint", None)
        return params

    def call(self, messages, tools=None, callbacks=None, available_functions=None, from_task=None, from_agent=None, response_model=None):
        max_attempts = 6
        for attempt in range(max_attempts):
            try:
                return super().call(
                    messages=messages,
                    tools=tools,
                    callbacks=callbacks,
                    available_functions=available_functions,
                    from_task=from_task,
                    from_agent=from_agent,
                    response_model=response_model
                )
            except Exception as e:
                error_str = str(e).lower()
                is_rate_limit = "rate_limit" in error_str or "rate limit" in error_str or "429" in error_str
                if is_rate_limit and attempt < max_attempts - 1:
                    # Groq tells us how long to wait, default to 10 + attempt * 5 if we can't parse it
                    sleep_time = 15 + attempt * 5
                    # Try to parse the sleep time from Groq error message e.g. "Please try again in 1.34s" or "Please try again in 15.639999999s."
                    import re
                    match = re.search(r"try again in ([\d\.]+)s", error_str)
                    if match:
                        sleep_time = float(match.group(1)) + 1.0 # Add 1s buffer
                    print(f"\n[GroqLLM] Rate limit reached. Sleeping for {sleep_time:.2f} seconds before retrying (attempt {attempt + 1}/{max_attempts})...")
                    time.sleep(sleep_time)
                else:
                    raise



inventory_agent = Agent(

    role="Inventory Management Agent",

    goal="""
    Analyze inventory demand trends,
    forecast future demand,
    determine products requiring replenishment,
    and recommend quantities.
    """,

    backstory="""
    You are an inventory planning expert.

    You receive today's inventory snapshot,
    store historical records,
    analyze demand growth,
    identify trending products,
    consider seasonal demand,
    and estimate replenishment quantities.

    Return only structured JSON.
    """,

    llm=GroqLLM(
        model="groq/llama-3.3-70b-versatile",  # 12K TPM (higher than 8b-instant's 6K)
        provider="litellm",
        additional_params={"num_retries": 5}
    ),

    verbose=True,

    tools=[
        InventoryAPITool(),
        StoreInventoryTool(),
        HistoricalSalesTool()
    ]
)
