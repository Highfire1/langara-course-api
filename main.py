import os
import sys
import logging
import uvicorn
import schedule

from parsers.SemesterParser import SemesterParser

from build import parse_build_data, update_latest_semester

if not os.path.exists("data/json/"):
    print("No data found. Downloading and parsing all data.")
    parse_build_data(getFromWeb=True)


# update semester data every 30 minutes
increment1 = 60 * 30
update_latest_semester()
schedule.every(increment1).seconds.do(update_latest_semester)

# rebuild big json file every 24 hours
increment2 = 60 * 60 * 24    
schedule.every(increment2).seconds.do(parse_build_data)


# uvicorn api.Api:app --host localhost --port 5000 --reload
if __name__ == "__main__":
    print("Launching uvicorn.")
    
    uvicorn.run("api.Api:app", host="0.0.0.0", port=5000)


