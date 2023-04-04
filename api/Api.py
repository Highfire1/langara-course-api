from fastapi import FastAPI, HTTPException
import json

from api.Enums import Years, Semesters


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/v1/courses/{year}/{semester}")
async def get_courses(year:Years, semester:Semesters):
    
    if year == 2023 and semester >= 30:
        raise HTTPException(status_code=404, detail="Semester data is not available yet.")
    
    try:
        with open (f"json/{year}{semester}.json", "r") as fi:
            data:json = json.loads(fi.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
        
    return data
