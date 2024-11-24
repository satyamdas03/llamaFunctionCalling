from typing import Literal, Optional
from pydantic import BaseModel, Field

class FunctionArguments(BaseModel):
    brightness: Optional[int] = Field(None, description="The desired brightness percentage (0-100).")
    volume: Optional[int] = Field(None, description="The desired volume percentage (0-100).")

class FunctionCall(BaseModel):
    name: Literal["set_brightness", "set_volume", "get_battery"]
    arguments: FunctionArguments
