# https://swing.langara.bc.ca/prod/hzgkcald.P_DisplayCatalog
from bs4 import BeautifulSoup, element
from pydantic import BaseModel
import requests
import os
import json

from schema.Catalogue import Catalogue, CatalogueCourse


'''
Parses the Langara Course Catalogue into json
'''
class CatalogueParser:
    
    def __init__(self) -> None:
        self.save_location = "data"
        self.page = None
        self.catalogue = None
        pass
            
    
    def loadPage(self, getPageFromWeb:bool = False, saveHTML:bool = True) -> None:
        
        file_location = f"{self.save_location}/catalogue/catalogue.html"
        
        # try to get saved file
        if not getPageFromWeb:
            try:
                with open(file_location, "r", encoding="utf-8") as p:
                    self.page = p.read()
                print(f"Loaded catalogue from {file_location}.")
                return
            except Exception as e:
                print("Could not load catalogue from disk: ", e)
                pass
        
        print("Fetching catalogue from the internet.")
        # else, get it from the web
        url = f"https://swing.langara.bc.ca/prod/hzgkcald.P_DisplayCatalog"
        r = requests.post(url)
        self.page = r.text
        
        # create dir if it doesn't exist
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        
        if saveHTML:
            with open(file_location, "w+", encoding="utf-8") as fi:
                fi.write(self.page)
        print("Catalogue fetched.")
        
        
    def parsePage(self) -> None:
        self.catalogue = Catalogue()
        
        soup = BeautifulSoup(self.page, 'lxml')

        coursedivs:list[element.Tag] = soup.find_all("div", class_="course")
        
        
        for div in coursedivs:
            h2 = div.findChild("h2").text
            title = div.findChild("b").text
            
            # the best way i can find to find an element with no tag            
            for e in div.children:
                if not str(e).isspace() and str(e)[0] != "<":
                    description = e.text.strip()
                    break
            
            h2 = h2.split()
            # h2 = ['ABST', '1100', '(3', 'credits)', '(3:0:0)']
            hours = h2[4].replace("(", "").replace(")", "").split(":")
            hours = {
                "lecture" : float(hours[0]),
                "seminar" : float(hours[1]),
                "lab" :     float(hours[2])
            }

            c = CatalogueCourse(
                subject=h2[0],
                course_code=int(h2[1]),
                credits=float(h2[2].replace("(", "")),
                hours=hours,
                title=title,
                description=description,
            )            
            self.catalogue.courses.append(c)
    
    def saveCourses(self):
        save = json.dumps(json.loads(self.catalogue.json()), default=vars, indent=4)
            
        file_location = f"{self.save_location}/catalogue/catalogue.json"
        
        # create dir if it doesn't exist
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        
        with open(file_location, "w+") as fi:
            fi.write(save)
        
    def LoadParseAndSave(self, getPageFromWeb:bool = False):
        self.loadPage(getPageFromWeb=getPageFromWeb)
        courses = self.parsePage()
        self.saveCourses()
        

if __name__ == "__main__":
    c = CatalogueParser()
    c.LoadParseAndSave()
    print("Done!")
