from typing import Literal, Optional
from pydantic import BaseModel, Field

class FunctionArguments(BaseModel):
    brightness: Optional[int] = Field(None, description="The desired brightness percentage (0-100).")
    volume: Optional[int] = Field(None, description="The desired volume percentage (0-100).")
    app_path: Optional[str] = Field(None, description="The path to the application to be opened.")
    drive: Optional[str] = Field(None, description="The drive to check for storage information.")
    city: Optional[str] = Field(None, description="The name of the city for weather updates.")
    category: Optional[str] = Field(None, description="The news category (e.g., general, technology, sports).")
    query: Optional[str] = Field(None, description="Search query for the web.")

class FunctionCall(BaseModel):
    name: Literal["set_brightness", "set_volume", "get_battery", "get_storage_info", "open_application", "get_weather", "get_latest_news", "search_web"]
    arguments: FunctionArguments
