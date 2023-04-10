from fastapi import HTTPException

from schema.Semester import Semester, Course, ScheduleEntry, Years, Semesters
from schema.CourseInfo import CourseInfo



async def get_courses(year:Years, semester:Semesters) -> Semester:
    pass


async def get_course_from_semester(year:Years, semester:Semesters, crn:int) -> Course:
    pass

async def get_course(subject: str, coursecode: int) -> CourseInfo:
    pass