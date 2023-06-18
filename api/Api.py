import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from schema.Semester import Semester, Years, Semesters, Course
from schema.CourseInfo import CourseInfo, CourseInfoAll


desc = "Gets course data from the Langara website. Data refreshes daily at midnight. Pull requests welcome!"

app = FastAPI(
    title="Langara Courses API (unofficial)",
    description=desc,
    contact={"name" : "Anderson T"},
    )



class ErrorMessage(BaseModel):
    message: str

@app.get(
    "/v1/courselist/{year}/{semester}", 
    summary="Get all courses in a semester.",
    description="Returns all courses for a given year and semester.",
    responses= {
        404: {"model" : ErrorMessage}
    },
    )
async def get_semester_courses(year:Years, semester:Semesters) -> Semester:
    
    #if year == 2023 and semester >= 30:
    #    raise HTTPException(status_code=404, detail="Semester data is not available yet.")
    
    try:
        with open (f"data/json/{year}{semester}.json", "r") as fi:
            data:json = json.loads(fi.read())
            
            return data
        
    except Exception as e:
        
        raise HTTPException(status_code=500, detail="Server error.")
        
    


@app.get(
    "/v1/courselist/{year}/{semester}/{crn}", 
    summary="Get a course from a semester.",
    description="Returns the course with a crn in the given year and semester.",
    responses= {
        404: {"model" : ErrorMessage}
    },
    )
async def get_course_from_semester(year:Years, semester:Semesters, crn:int) -> Course:
        
    # TODO: put other error codes in the schema
    #if year == 2023 and semester >= 30:
    #    raise HTTPException(status_code=404, detail="Semester data is not available yet.")
    
    try:
        
        with open (f"data/json/{year}{semester}.json", "r") as fi:
            s = Semester()
            s.parse_file(f"data/json/{year}{semester}.json")
            
            for c in s.courses:
                if c.crn == crn:
                    return c
                
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong: " + e)
    
    
    raise HTTPException(status_code=404, detail="CRN not found.")
        

@app.get(
    "/v1/courses/all", 
    summary="Get information about all courses.",
    #description="Returns information about a course.",
    responses= {
    },
    )
async def get_courseInfo() -> CourseInfoAll:
    return CourseInfoAll.parse_file("data/build/courseInfo.json")



@app.get(
    "/v1/courses/{subject}/{course_code}", 
    summary="Gets information about a course.",
    description="Returns information about a course.",
    responses= {
        404: {"model" : ErrorMessage}
    },
    )
async def get_course(subject: str, course_code: int) -> CourseInfo:
    global courses
    
    if courses == None:
        courses = CourseInfoAll.parse_file("data/build/courseInfo.json")
                
    for c in courses.courses:
        
        if subject == c.subject and course_code == c.course_code:
            return c
    
    raise HTTPException(status_code=404, detail="Course not found.")

courses = CourseInfoAll.parse_file("data/build/courseInfo.json")