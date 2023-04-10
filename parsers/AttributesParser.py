# https://swing.langara.bc.ca/prod/hzgkcald.P_DisplayCatalog
from bs4 import BeautifulSoup, element
from pydantic import BaseModel
import requests
import os
import json

from schema.Attribute import Attributes, Attribute
from schema.CourseInfo import attributes as attr

'''
Parses the Langara Course attributes into json
https://swing.langara.bc.ca/prod/hzgkcald.P_DispCrseAttr#A

run with 
s = AttributesParser()
s.LoadParseAndSave()
'''
class AttributesParser:
    
    def __init__(self) -> None:
        self.save_location = "data"
        self.page = None
        self.attributesObj:Attributes = None
        pass
            
    
    def loadPage(self, getPageFromWeb:bool = False, saveHTML:bool = True) -> None:
        
        file_location = f"{self.save_location}/attributes/attributes.html"
        
        # try to get saved file
        if not getPageFromWeb:
            try:
                with open(file_location, "r", encoding="utf-8") as p:
                    self.page = p.read()
                print(f"Loaded attributes from {file_location}.")
                return
            except Exception as e:
                print("Could not load attributes from disk: ", e)
                pass
        
        print("Fetching attributes from the internet.")
        # else, get it from the web
        url = f"https://swing.langara.bc.ca/prod/hzgkcald.P_DispCrseAttr#A"
        r = requests.post(url)
        self.page = r.text
        
        # create dir if it doesn't exist
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        
        if saveHTML:
            with open(file_location, "w+", encoding="utf-8") as fi:
                fi.write(self.page)
        print("Attributes fetched.")
        
        
    def parsePage(self) -> None:
        self.attributesObj:Attributes = Attributes(attributes=[])
        
        soup = BeautifulSoup(self.page, 'lxml')

        # skip the first table which is the form for filtering entries
        table_items:list[element.Tag] = soup.find_all("table")[1].find_all("td")
        
                
        # convert to str, bool, bool, bool, etc
        for i in range(len(table_items)):
            table_items[i] = table_items[i].text
            
            if table_items[i] == "Y":
                table_items[i] = True
            elif table_items[i] == "&nbsp" or table_items[i].isspace():
                table_items[i] = False
        
        
        i = 0
        while i < len(table_items):
            
            
            self.attributesObj.attributes.append(Attribute(
                subject = table_items[i].split(" ")[0],
                course_code = table_items[i].split(" ")[1],
                attributes = {
                    "AR" : table_items[i+1],
                    "SC": table_items[i+2],
                    "HUM": table_items[i+3],
                    "LSC": table_items[i+4],
                    "SCI": table_items[i+5],
                    "SOC": table_items[i+6],
                    "UT": table_items[i+7],  
                 
                },
            ))
                        
            i += 8
            
    
    def saveCourses(self):        
        save = self.attributesObj.json(indent=4)
            
        file_location = f"{self.save_location}/attributes/attributes.json"
        
        # create dir if it doesn't exist
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        
        with open(file_location, "w+") as fi:
            fi.write(save)
        
    def LoadParseAndSave(self):
        self.loadPage()
        self.parsePage()
        self.saveCourses()