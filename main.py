import os
import sys
import logging
import uvicorn
import schedule

from parsers.SemesterParser import SemesterParser

from build import parse_build_data

# refresh current semester every 24 hours
def daily_update():
    logging.info("Fetching fresh course data from the Langara website.")
    p = SemesterParser(2021, 30)
    p.loadPageFromWeb()
    p.parseAndSave()


if not os.path.exists("data/json/"):
    print("No data found. Downloading and parsing all data.")
    parse_build_data(getFromWeb=True)
    
#daily_update()
schedule.every().day.at("00:00:00").do(daily_update)

# uvicorn api.Api:app --host localhost --port 5000 --reload
if __name__ == "__main__":
    print("Launching uvicorn.")
    
    uvicorn.run("api.Api:app", host="0.0.0.0", port=5000)


