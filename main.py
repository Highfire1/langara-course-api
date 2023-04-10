import os
import logging
import uvicorn
import schedule
from builders.CourseInfoBuilder import CourseInfoBuilder
from parsers.CatalogueParser import CatalogueParser

from parsers.SemesterParser import SemesterParser
from parsers.TransferParser import TransferParser
from parsers.AttributesParser import AttributesParser

def parse_build_data():
    s = SemesterParser()
    s.loadParseSaveAll()
    
    p = AttributesParser()
    p.LoadParseAndSave()
    
    c = CatalogueParser()
    c.LoadParseAndSave()
    
    #TransferParser.transfer_courses_generator()
    #TransferParser.ahk_data_generator()
    TransferParser.parse_and_save_transfer_pdfs()
    
    c = CourseInfoBuilder()
    c.hydrateBuildSave()

# refresh current semester every 24 hours
# TODO: implement smarter way to keep data updated
def daily_update():
    logging.info("Fetching fresh course data from the Langara website.")
    
    #p = SemesterParser(2023, 20)
    #p.loadPageFromWeb()
    #p.parseAndSave()
    

if not os.path.exists("data/json/"):
    print("No data found. Downloading and parsing all course data.")
    SemesterParser.loadParseSaveAll()
    

daily_update()
schedule.every().day.at("00:00:00").do(daily_update)

# uvicorn api.Api:app --host localhost --reload
uvicorn.run("api.Api:app", host="0.0.0.0", port=5000)


