from typing import Literal, Optional
from pydantic import BaseModel, Field

class FunctionArguments(BaseModel):
    brightness: Optional[int] = Field(None, description="The desired brightness percentage (0-100).")
    volume: Optional[int] = Field(None, description="The desired volume percentage (0-100).")
    app_path: Optional[str] = Field(None, description="The path to the application to be opened.")
    drive: Optional[str] = Field(None, description="The drive to check for storage information.")
    city: Optional[str] = Field(None, description="The name of the city for weather updates.")
    category: Optional[str] = Field(None, description="The news category (e.g., general, technology, sports).")
    query: Optional[str] = Field(None, description="Search query for the web.")  # Correctly supports search_web
    state: Optional[str] = Field(None, description="State to toggle (on/off).")
    text: Optional[str] = Field(None, description="Text to read aloud.")
    task: Optional[str] = Field(None, description="The task description for the reminder.")
    date_time: Optional[str] = Field(None, description="The date and time for the task in 'YYYY-MM-DD HH:MM:SS' format.")


class FunctionCall(BaseModel):
    name: Literal["set_brightness", "set_volume", "get_battery", "get_storage_info", "open_application", "get_weather", "get_latest_news", "search_web", "toggle_wifi", "show_connected_wifi", "toggle_bluetooth", "list_paired_bluetooth_devices", "toggle_night_light", "read_screen_contents_aloud","schedule_task",]
    arguments: FunctionArguments
