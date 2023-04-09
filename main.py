import os
import logging
import uvicorn
import schedule

from parsers.SemesterParser import SemesterParser


# refresh current semester every 24 hours
# TODO: implement smarter way to keep data updated
def fetch_course_data():
    logging.info("Fetching fresh course data from the Langara website.")
    
    #p = SemesterParser(2023, 20)
    #p.loadPageFromWeb()
    #p.parseAndSave()
    


if not os.path.exists("data/json/"):
    print("No data found. Downloading and parsing all course data.")
    SemesterParser.loadParseSaveAll()
    

fetch_course_data()
schedule.every().day.at("00:00:00").do(fetch_course_data)

# uvicorn api.Api:app --host localhost --reload
uvicorn.run("api.Api:app", host="0.0.0.0", port=5000)
