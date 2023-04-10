import os

from schema.CourseInfo import CourseInfoAll, CourseInfo
from schema.Attribute import Attributes, Attribute
from schema.Catalogue import Catalogue, CatalogueCourse
from schema.Semester import Semester, Course, ScheduleEntry


'''
Compiles data and saves into a CourseInfoAll
'''

class CourseInfoBuilder:
    def __init__(self) -> None:
        self.all_courses:CourseInfoAll = None
        
        self.attributes:Attributes = None
        self.catalogue:Catalogue = None
        self.semesters:list[Semester] = None

    def hydrate(self):
        self.attributes = Attributes.parse_file("data/attributes/attributes.json")
        self.catalogue = Catalogue.parse_file("data/catalogue/catalogue.json")
        
        self.semesters = []
        for fi in os.listdir("data/json"):
            print(fi)
        
        
        
    
    def build(self):
        self.hydrate()
        self.all_courses = CourseInfoAll
        
        
        