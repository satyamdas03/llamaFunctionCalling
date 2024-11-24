from typing import Literal, Optional
from pydantic import BaseModel, Field

class FunctionArguments(BaseModel):
    brightness: Optional[int] = Field(None, description="The desired brightness percentage (0-100).")
    volume: Optional[int] = Field(None, description="The desired volume percentage (0-100).")
    app_path: Optional[str] = Field(None, description="The path to the application to be opened.")
    drive: Optional[str] = Field(None, description="The drive to check for storage information.")

class FunctionCall(BaseModel):
    name: Literal["set_brightness", "set_volume", "get_battery", "get_storage_info", "open_application"]
    arguments: FunctionArguments
