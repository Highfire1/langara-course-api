import datetime
import sys
import logging
import os
import requests

from dotenv import load_dotenv
load_dotenv()


from builders.AllBuilder import AllBuilder
from builders.CourseInfoBuilder import CourseInfoBuilder
from parsers.CatalogueParser import CatalogueParser
from parsers.SemesterParser import SemesterParser
from parsers.TransferParser import TransferParser
from parsers.AttributesParser import AttributesParser
from schema.Semester import Semester


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
    # unnessecary until data is refreshed
    #TransferParser.parse_and_save_transfer_pdfs()
    
    
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
    
    oldData = Semester.parse_file(f"data/json/{year}{semester}.json")
    
    p = SemesterParser(year, semester)
    p.loadPageFromWeb()
    newData = p.parseAndSave()    
    
    if len(oldData.courses) < len(newData.courses):
        
        out = []
        
        
        for course in newData.courses:
            exists = False
            
            for c in oldData.courses:
                
                if c.crn == course.crn:
                    exists = True
                    break
            
            
            
            if not exists:
                #print(course.crn, " does not exist")
                msg = f"{course.crn} **{course.subject} {course.course_code}** {course.section} {course.title}\n"
                for s in course.schedule:
                    msg += f"{s.days} {s.time} {s.type.name} {s.room} {s.instructor}\n"
                msg += "\n"
                out.append(msg)
        
        
        if out != []:            
            send_webhook(title="New sections found:",content="\n".join(out))
                

#latest_semester_update()
#sys.exit()


def send_webhook(title:str, content:str):
    
    url = os.environ.get("DISCORD_WEBHOOK_URL")
    
    # TODO: more nuanced way to make webhooks optional
    if url == None:
        print("Warning: No discord webhook provided. Set an environmental variable names DISCORD_WEBHOOK_URL.")
    
        
    if len(content) > 4000:
        content = content[:3990] + "\nCONTENT TRUNCATED."
    
    data = {
    "content" : "",
    "username" : "Langara Course Updates"
    }
    
    data["embeds"] = [
    {
        "description" : f"{content}",
        "title" : f"{title}"
    }
    ]
    
    result = requests.post(url, json = data)
    
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print(f"{title} delivered to discord with code {result.status_code}.")


if __name__ == "__main__":
    #UPDATE_ALL(getFromWeb=False) 
    
    update_latest_semester()