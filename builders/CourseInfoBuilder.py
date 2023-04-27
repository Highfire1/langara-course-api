import os

from pydantic import BaseModel

from schema.CourseInfo import CourseInfoAll, CourseInfo, Grade, availability, Prerequisite, PrereqEnum
from schema.Attribute import Attributes, Attribute
from schema.Catalogue import Catalogue, CatalogueCourse
from schema.Transfer import Transfers, Transfer
from schema.Semester import Semester, Course, ScheduleEntry, RPEnum


'''
Compiles data and saves into a CourseInfoAll
'''

class CourseInfoBuilder:
    def __init__(self) -> None:
        self.all_courses:CourseInfoAll = None
        
        self.attributes:Attributes = None
        self.catalogue:Catalogue = None
        self.semesters:list[Semester] = None
        self.transfers:Transfers = None

    def hydrate(self):
        self.attributes = Attributes.parse_file("data/attributes/attributes.json")
        self.catalogue = Catalogue.parse_file("data/catalogue/catalogue.json")
        self.transfers = Transfers.parse_file("data/transfer/transfers.json")

        self.semesters = []
        #
        files = list(os.listdir("data/json"))
        files.sort() # order 200010.json -> 202320.json
        for fi in files:
            self.semesters.append(Semester.parse_file(f"data/json/{fi}"))
        
        
        courses:list[Course] = []
        for s in self.semesters:
            courses += s.courses
        
        unique_courses = []
        for c in courses:
            if f"{c.subject} {c.course_code}" not in unique_courses:
                unique_courses.append(f"{c.subject} {c.course_code}")
                
                
        years = 5
        r_courses:list[Course] = []
        for s in self.semesters[-3*years:]:
            r_courses += s.courses
        
        r_unique_courses = []
        for c in r_courses:
            if f"{c.subject} {c.course_code}" not in r_unique_courses:
                r_unique_courses.append(f"{c.subject} {c.course_code}")
                
                
        unique_transfers = []
        for c in self.transfers.courses:
            if f"{c.subject} {c.course_code}" not in unique_transfers:
                unique_transfers.append(f"{c.subject} {c.course_code}")
            
        '''
        Found 1245 courses in the course catalogue.
        Found attributes for 689 courses.
        Found 71 semesters with 59400 courses and 1773 unique courses.
        17051 courses and 1113 unique courses were offered in the last 5 years.
        Found 11882 transfer agreements for 841 unique courses. 
        '''
        
        print(f"Found {len(self.catalogue.courses)} courses in the course catalogue.")
        print(f"Found attributes for {len(self.attributes.attributes)} courses.")
        print(f"Found {len(self.semesters)} semesters with {len(courses)} courses and {len(unique_courses)} unique courses.")
        print(f"{len(r_courses)} courses and {len(r_unique_courses)} unique courses were offered in the last {years} years.")
        print(f"Found {len(self.transfers.courses)} transfer agreements for {len(unique_transfers)} unique courses.")
        print("------------------------")
    
    def build(self):        
        self.all_courses = CourseInfoAll(courses=[])
        
        unique_courses:list[str] = []
        for s in self.semesters:
            for c in s.courses:
                if f"{c.subject} {c.course_code}" not in unique_courses:
                    unique_courses.append(f"{c.subject} {c.course_code}")
                    
        unique_courses.sort()
        
        #unique_courses = unique_courses[:200]
        
        print(f"Now building information for {len(unique_courses)} courses.....")
        
        oldsubj = None
        i = 0
        
        for course in unique_courses:
            subject = course.split(" ")[0]
            
            if oldsubj != subject:
                print(f"Loading courses for {subject} ({i}/{len(unique_courses)}).")
                oldsubj = subject
            i += 1
            
            course_code = int(course.split(" ")[1])
            restrictions:RPEnum = None
            credits:float = None
            title:str = None
            description:str = None
            hours: dict[str, float] = None
            add_fees:float = None
            rpt_limit:int = None
            
            
            
            semesters_offered:list[str] = []
            
            for s in self.semesters:
                for c in s.courses:
                    if subject == c.subject and course_code == c.course_code:
                        semesters_offered.append(f"{s.year}{s.semester}")
                        restrictions = c.RP
                        credits = c.credits
                        title = c.title
                        add_fees = c.add_fees
                        rpt_limit = c.rpt_limit
                        break
            
            if title == None:
                raise Exception(f"Could not find course {subject} {course_code}.")
            
            for c in self.catalogue.courses:
                if subject == c.subject and course_code == c.course_code:
                    title = c.title
                    description = c.description
                    credits = c.credits
                    hours = c.hours
            
            #if hours == None:
            #    print(f"Did not find {subject} {course_code} in the catalogue.")
            
            avail:availability = availability.unknown
            
            terms = []
            for s in semesters_offered:
                if int(s[:4]) >= 2019: 
                    # only consider recent terms
                    terms.append(int(s[-2:]))
            
            if len(terms) == 0:
                avail = availability.discontinued
            
            elif len(set(terms)) == 1:
                if terms[0] == 10:
                    avail = availability.spring
                if terms[0] == 20:
                    avail = availability.summer
                if terms[0] == 30:
                    avail = availability.fall
            
            elif len(set(terms)) == 3:
                avail = availability.all
            
            elif abs(terms.count(10)-terms.count(20)) <= 1 and terms.count(10) >= 2 and terms.count(30) == 0:
                avail = availability.springsummer
            elif abs(terms.count(10)-terms.count(30)) <= 1 and terms.count(10) >= 2 and terms.count(20) == 0:
                avail = availability.springfall
            elif abs(terms.count(30)-terms.count(20)) <= 1 and terms.count(30) >= 2 and terms.count(10) == 0:
                avail = availability.summerfall
            
            #print(f"{avail.value}\t\t{terms}")  
            
            transfers:list[Transfer] = []
            for c in self.transfers.courses:
                if subject == c.subject and course_code == c.course_code:
                    transfers.append(c)
            
            attr:dict[str, bool] = None
            for c in self.attributes.attributes:
                if subject == c.subject and course_code == c.course_code:
                    attr = c.attributes
                    break
                
            #if attr == None:
            #    print(f"No attributes for {subject} {course_code}.")
            
            

            restrict = None
            
            if description != None and "restricted to" in description and "This course is designed for (although not restricted to)" not in description:
                restrict = description.split("restricted to")[1]
                restrict = restrict.split(".")[0]
                
                if "following programs: ":
                    restrict = restrict.split("following programs: ", maxsplit=1)[-1]
                    
                if "to the " in restrict:
                    restrict = restrict.split("to the ")[-1]   
                    
                restrict = restrict.strip()             
            
            prereq = None
            if description != None and "Prerequisite(s): " in description:
                #print(" >", description.split("Prerequisite(s): ")[-1])
                prereq = self.parsePrerequisite(description.split("Prerequisite(s): ")[-1])
            
            c = CourseInfo(
                RP = restrictions,
                subject = subject,
                course_code = course_code,
                credits = credits,
                title = title,
                description = description,
                hours = hours,
                add_fees = add_fees,
                rpt_limit = rpt_limit,
                availability = avail,
                prev_offered = semesters_offered,
                attributes = attr,
                transfer = transfers,
                
                prerequisites = prereq,
                restriction = restrict,
                
            )
            self.all_courses.courses.append(c)
                        
            #print(c)
        print("Done!")
    
    
    
    def parsePrerequisite(self, text:str) -> Prerequisite:
        prereq = Prerequisite(type=PrereqEnum.ALL_OF, requirements=[])
        
        # get rid of text
        text = text.split("Prerequisite(s): ")[-1]
        # there are random newlines in my data for some reason
        text = text.replace("\n", " ")
        
        # get rid of Note: because they aren't a prerequisite
        if "Note: " in text:
            text = text.split("Note: ")[0]
            
        text = text.replace("; and ", "SPLIT")
        text = text.replace("Corequisite(s):", "SPLITCorequisite(s):")
        text = text.split("SPLIT")
        
        i = -1
        while i < len(text) - 1:
            i += 1
            item = text[i]
            
            # special cases
            if "Corequisite(s)" in item:
                
                prereq.requirements.append(
                    Prerequisite(type=PrereqEnum.COREQ, requirements=[
                        self.splitter(item.replace("Corequisite(s): ", ""))
                ]))
                continue
            
            # ONE COURSE USES THIS WEIRD FORMAT
            if "One of the following prerequisite combinations" in item:
                # TODO: fix this case
                i += 1
                continue 
                
            #print("->", item)
            prereq.requirements.append(self.splitter(item))
            #print("|>", prereq)
            prereq = self.flattenPrereq(prereq)
            #print("|>", prereq)
        
        
        #print("-----------\n\n-----------")
    
        
        return prereq
    
    # only takes very specific strings e.g.
    # One of the following: LET 3 (or LPI equivalent); LEAP 8; a minimum "C+" grade in English First Peoples 12,
    # CHEM 1114, 1117, or 1217
    # APPL 4110.
    # Any 15 university-transferable credits. This course is not intended for first-year students.
    # Mathematics 12 or Precalculus 12.
    def splitter(self, item:str) -> Prerequisite:
        
        if "one of" in item or " or " in item:
            mode = PrereqEnum.ONE_OF
        elif "all of" in item or "both of" in item:
            mode = PrereqEnum.ALL_OF  
        else:
            mode = PrereqEnum.ALL_OF
        
        prereq = Prerequisite(type=mode, requirements=[])
            
        # regexes aren't real
        item = item.replace(";", "SPLIT")
        item = item.replace(":", "SPLIT")
        item = item.replace(",", "SPLIT")
        item = item.replace(";", "SPLIT")
        item = item.replace(".", "SPLIT")
        
        item = item.replace(" or ", "SPLIT")
        item = item.replace(" and ", "SPLIT")
        
        items = item.split("SPLIT")
        items = list(filter(None, items)) # remove empty items
        
        default_grade = None
        default_subj = ""
        
        for i in items:
            i = i.strip()
            
            #print("=>", i)
            
            
            
            if "ne of the following" in i or "ll of the following" in i:
                if "grade" in i:
                    default_grade = i.split('"')[1]
                continue
            
            elif "equivalent" in i and "LET" not in i:
                prereq.requirements.append(Grade(course="Or equivalent."))
                
            if "may be taken concurrently" in i:
                # idk if this counts as a prerequisite
                # TODO: fix later
                prereq.requirements.append(Grade(course=i.replace(".", "").strip()))
            
            if "permission of department" in i:
                prereq.requirements.append(Grade(course=i.replace(".", "").strip()))
                
            
            elif '"' in i:
                s = i.split('"')
                course = s[-1].split("in ")[-1]
                course = course.replace(".", "")
                course = course.strip()
                                
                prereq.requirements.append(Grade(grade=s[1], course=course))
                default_subj = course[:4]
                default_grade = s[1]
            
            elif default_grade != None or ( len(i) == 4 and i.isdecimal() ):
                i = i.replace(".", "")
                add = ""
                if len(i) >= 4 and i[:4].isdecimal():
                    add = default_subj + " "
                prereq.requirements.append(Grade(grade=default_grade, course=add+i))
                if default_subj == "":
                    default_subj = i[:4]
            
            else:
                prereq.requirements.append(Grade(course=i))

            #print(prereq.requirements[-1])
            
        return prereq
    
    # flatten e.g. "ALL OF -> ONE OF CPSC 1000" to "ALL OF -> CPSC 1000"
    # shouldn't be neccessary but my code sucks
    # doesn't even work properly
    def flattenPrereq(self, prereq:Prerequisite) -> Prerequisite:        
        # can't flatten grades
        if type(prereq.requirements[0]) == Grade:
            return prereq
        
        new_prereq = Prerequisite(type=prereq.type, requirements=[])

        
        for i in range(len(prereq.requirements)):
            prereq.requirements[i] = self.flattenPrereq(prereq.requirements[i])
            
        found = []
            
        for p in prereq.requirements:
            
            if p.type not in found:
                found.append(p.type)
                new_prereq.requirements.append(p)
            else:
                
                for p2 in prereq.requirements:
                    if p2.type == p.type:
                        p2.requirements += p.requirements
                        break
        
        #print("==>", prereq, "\n")
         
        return new_prereq
    
    def saveCourses(self):        
        save = self.all_courses.json(indent=4)
            
        file_location = f"data/build/courseInfo.json"
        
        # create dir if it doesn't exist
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        
        with open(file_location, "w+") as fi:
            fi.write(save)
    
    def hydrateBuildSave(self):
        self.hydrate()
        self.build()
        self.saveCourses()
        
        