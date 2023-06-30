import datetime
import sys
import logging
import os


from builders.AllBuilder import AllBuilder
from builders.CourseInfoBuilder import CourseInfoBuilder
from parsers.CatalogueParser import CatalogueParser
from parsers.SemesterParser import SemesterParser
from parsers.TransferParser import TransferParser
from parsers.AttributesParser import AttributesParser


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
    
    a = AllBuilder()
    a.hydrateBuildSave()



# WARNING: this takes 9 minutes and 30 seconds to finish on my laptop
# DOUBLE WARNING: this takes 18 minutes if you download new data
# TODO: make this faster (?)
def UPDATE_ALL(getFromWeb = False): 
    parse_build_data(getFromWeb=getFromWeb)
    update_latest_semester()


# call this function daily 
# it checks if data for a new semester is available
# then updates data for the current semester
# very primitive, should probably be redone properly in the future
def update_latest_semester():
    
    # check to see if a newer semester is available
    pages = os.listdir("data/pages")
    
    assert(len(pages) > 0)
    
    pages.sort()    
    year = int(pages[-1][0:4])
    semester = int(pages[-1][4:6])
    
    # calculate next semester
    if semester == 30:
        year += 1
        semester = 10
    else:
        semester += 10
    
    p = SemesterParser(year, semester)
    p.loadPageFromWeb(saveHTML=False)
    
    
    if "No courses were found that meet your search criteria" in p.page or "Seats Avail" not in p.page:
        logging.info(f"No information found for {year}{semester}.")
    else:
        logging.info(f"Information for new semester {year}{semester} found!")
        p.parseAndSave()
        update_latest_semester() # hooray for recursiveness
        
    
    # get data for current semester
    pages = os.listdir("data/pages")
    pages.sort()    
    year = int(pages[-1][0:4])
    semester = int(pages[-1][4:6])
        
    assert datetime.date.today().year + 1 >= year, f"Semester {year}{semester} is too far in the future!" # sanity check that year is correct
    
    p = SemesterParser(year, semester)
    p.loadPageFromWeb()
    p.parseAndSave()

#latest_semester_update()
#sys.exit()

if __name__ == "__main__":
    UPDATE_ALL(getFromWeb=False) 