from pydantic import BaseModel

from api.Enums import Years, Semesters

class ScheduleEntry(BaseModel):
    type: str
    days: str
    time: str
    start: str | None
    end: str | None
    room: str
    instructor: str
    
    class Config:
        schema_extra = {
            "example": {
                "type" : "Lecture",
                "days" : "M-W----",
                "time" : "1030-1220",
                "start": None,
                "end" : None,
                "room": "A136B",
                "instructor": "Adam Solomonian"
            }
        }
    
class Courses(BaseModel):
    RP : str
    seats: str
    waitlist: str
    crn: str
    subject: str
    course: str
    section: str
    credits: str
    title: str
    add_fees: str
    rpt_limit: str
    notes: str | None
    schedule:list[ScheduleEntry]
    
    class Config:
        schema_extra = {
            "example": {
                "RP" : " ",
                "seats" : "29",
                "waitlist" : "25",
                "crn" : "20533",
                "subject" : "ANTH",
                "course" : "1120",
                "section" : "001",
                "credits" : "3.00",
                "title" : "Intro to Cultural Anthropology",
                "add_fees" : " ",
                "rpt_limit" : "-",
                "notes" : None,
                "schedule" : [ScheduleEntry.Config.schema_extra["example"]],
            }
        }

class Semester(BaseModel):
    datetime_retrieved: str
    year: Years
    semester: Semesters
    courses_first_day: str
    courses_last_day: str
    courses: list[Courses]
    
    
    class Config:
        schema_extra = {
            "example": {
                "datetime_retrieved" : "2023-04-04",
                "year": "2023",
                "semester" : "20",
                "courses_first_day" : "2023-5-08",
                "courses_last_day" : "2023-8-31",
                "courses" : [Courses.Config.schema_extra["example"]]
            }
        }
