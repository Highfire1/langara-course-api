import os

from pydantic import BaseModel

from schema.CourseInfo import CourseInfoAll, CourseInfo
from schema.Semester import Semester, Course


class AllBuilder:
    def __init__(self) -> None:
        self.all_courses:CourseInfoAll = None  
        self.semesters:list[Semester] = None

    def hydrate(self):
        
        self.all_courses = CourseInfoAll.parse_file("data/build/courseInfo.json")
        
        self.semesters = []
        for filename in os.listdir("data/json/"):
            self.semesters.append(Semester.parse_file("data/json/" + filename))
                
    
    # WARNING : takes ~ 5 minutes to run right now
    # TODO: speed this up
    def build(self):
        for i, course in enumerate(self.all_courses.courses):
            
            print(f"Building {i}/{len(self.all_courses.courses)}")
            
            course.offered = []
            
            for semester in self.semesters:
                for c in semester.courses:
                    c.yearsemester = f"{semester.year}{semester.semester}"
                    
                    if c.subject == course.subject and c.course_code == course.course_code:
                        course.offered.append(c)
                        
        
            
    def saveCourses(self):        
        save = self.all_courses.json(indent=4)
            
        file_location = f"data/build/allInfo.json"
        
        # create dir if it doesn't exist
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        
        with open(file_location, "w+") as fi:
            fi.write(save)
    
    def hydrateBuildSave(self):
        self.hydrate()
        self.build()
        self.saveCourses()
        