import json

from fastapi import FastAPI, HTTPException

from api.Enums import Years, Semesters
from api.Schema import Semester

desc = "Gets course data from the Langara website. Data refreshes daily at midnight. Pull requests welcome!"

app = FastAPI(
    title="Langara Courses API (unofficial)",
    description=desc,
    contact={"name" : "Anderson T"}
    )


@app.get(
    "/v1/courses/{year}/{semester}", 
    response_model=Semester,
    description="Returns all courses for a given year and semester."
    )
async def get_courses(year:Years, semester:Semesters):
    
    # TODO: put other error codes in the schema
    if year == 2023 and semester >= 30:
        raise HTTPException(status_code=404, detail="Semester data is not available yet.")
    
    try:
        with open (f"json/{year}{semester}.json", "r") as fi:
            data:json = json.loads(fi.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
        
    return data
