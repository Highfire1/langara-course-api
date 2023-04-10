import os
import logging
import uvicorn
import schedule
from builders.CourseInfoBuilder import CourseInfoBuilder
from parsers.CatalogueParser import CatalogueParser

from parsers.SemesterParser import SemesterParser
from parsers.TransferParser import TransferParser
from parsers.AttributesParser import AttributesParser

"""
Force fetching data from the internet.
This may take some time and is likely not neccessary.
"""
    

"""
Parse all data.
May fetch content from the internet if not found in data/
May take some time.
"""
def parse_build_data(getFromWeb = False):
    SemesterParser.loadParseSaveAll(getPagesFromWeb=getFromWeb)

    p = AttributesParser()
    p.LoadParseAndSave(getPageFromWeb=getFromWeb)
    
    c = CatalogueParser()
    c.LoadParseAndSave(getPageFromWeb=getFromWeb)
    
    # The process for fetching transfer data is currently
    # very manual and is not automated.
    
    #TransferParser.transfer_courses_generator()
    #TransferParser.ahk_data_generator()
    TransferParser.parse_and_save_transfer_pdfs()
    
    
    c = CourseInfoBuilder()
    c.hydrateBuildSave()

# refresh current semester every 24 hours
def daily_update():
    logging.info("Fetching fresh course data from the Langara website.")
    #p = SemesterParser(2023, 20)
    #p.loadPageFromWeb()
    #p.parseAndSave()
    




if not os.path.exists("data/json/"):
    print("No data found. Downloading and parsing all data.")
    parse_build_data(getFromWeb=True)
    
daily_update()
schedule.every().day.at("00:00:00").do(daily_update)

# uvicorn api.Api:app --host localhost --port 5000 --reload
uvicorn.run("api.Api:app", host="0.0.0.0", port=5000)


