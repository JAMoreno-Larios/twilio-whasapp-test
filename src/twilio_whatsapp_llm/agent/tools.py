import datetime

from langchain.tools import tool


@tool
def create_appointment(date: str) -> str:
    """Creates an appointment"""
    return f"Appointment created for {date}"


@tool
def add_numbers(a: float, b: float) -> str:
    """Add two numbers"""
    return str(a + b)


@tool
def find_appointment(date: str) -> str:
    """Finds if an appointment was made for the given date"""
    return f"Appointment found for {date}"


@tool
def get_today_date() -> str:
    """Returns today's date"""
    return datetime.datetime.today().strftime("%y-%m-%d")


TOOLS = [create_appointment, find_appointment, add_numbers, get_today_date]
