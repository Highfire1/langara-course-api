import os

from schema.CourseInfo import CourseInfoAll, CourseInfo, availability, Prerequisite
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
        
        #unique_courses = unique_courses[:100]
        
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
                prereq = self.parsePrerequisite(description)
            
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
    
    
    
    def parsePrerequisite(self, text:str) -> str:
        text = text.split("Prerequisite(s): ")[-1]
        
        return text
        
        print(text)

        conditions = []
        
        known_conditions = {
            "; or permission of the instructor." : "or permission of the instructor.",
            
            "Permission of the instructor." : "Permission of the instructor.",
            
            "Will be announced in the Registration Guide and Course Schedule." : "Will be announced in the Registration Guide and Course Schedule."
            
        }
        
        for string in known_conditions:
            if string in text:
                text = text.replace(string, "")
                conditions.append(known_conditions[string])
        
        
                
        if "Corequisite(s):" in text:
            text = text.split("Corequisite(s):")
            conditions.append("Corequisite(s):" + text[1])
            text = text[0].strip()
        
        # todo: fix later
        if "China or Taiwan" in text:
            conditions.append(text)
            return
        if "\n\n" in text:
            r = text.split("\n\n")
            text = r[0]
            conditions.append(text[1])
        
        text = text.replace(";", "SPLIT")
        #text = text.replace(".", "SPLIT") DOESN'T WORK
        text = text.split("SPLIT")
        
        print(text)
        
        for i, line in enumerate(text):
            line = line.strip()
            
            if line.isspace():
                continue
            
            overrides = [
                # Completion of the third year of the Bachelor of Science in Bioinformatics
                "Bachelor",  
                # BBA courses
                "ompletion of a minimum of",
                "Priority registration in this course is offered",
                'At least one course in',
                'or permission of ',
                'department permission',
                'Successful completion or concurrent registration in',
                'must achieve a minimum',
                'students who need to reinforce their grammar can enrol concurrently',
                # pain and suffering
                'Enrolment limited to students of the Study in Greece program',
                'Must be enrolled in the journalism program, unless otherwise indicated in the Registration Guide and Course Schedule',
                'Post-Degree Diploma in Web and Mobile App Design and Development',
                'Registration in this course is restricted to students admitted to Post-Degree Diploma programs with a co-op work term option',
                # english requirements are horrible
                'English Studies 12',
                'LET',
                'LPI',
                "IELTS",
                'TOEFL',
            ]
            cont = False
            for t in overrides:
                if t in line:
                    conditions.append(line)
                    cont = True
            
            if cont:
                continue
                        
            if line.strip().startswith("and"):
                conditions.append(line)
                continue
            
            print("LINE", line)

            parsed = False

            for mark in ["in one of the following", "in all of the following", "in one of", "in all of", " in both ", " in ", "and an "]:
                
                if mark in line:
                    split = line.split(mark, maxsplit=1)
                                                            
                    grade = split[0]
                    # WHY IS THERE CURLY QUOTE
                    if '“' in grade:
                        grade = grade.split('“')[1].split('”')[0]
                    else:
                        grade = grade.split('"')[1]
                
                    courses = split[1]
                    courses = courses.replace("and", "SPLIT")
                    courses = courses.replace("or", "SPLIT")
                    courses = courses.replace(",", "SPLIT")
                    courses = courses.split("SPLIT")
                    
                    courses[0] = courses[0].replace(": ", "")
                    subject = courses[0][0:4]
                    
                    courses[-1] = courses[-1].replace(".", "")
                    
                    for j, item in enumerate(courses):
                        courses[j] = item.strip()
                        
                        if courses[j][0:4].isnumeric():
                            courses[j] = subject + " " + courses[j]
                    
                    if "one of" in line or " or " in line:
                        mode = "one of"
                    elif "all of" in line or "both of" in line:
                        mode = "all of"         
                    else:
                        mode = "all of"
                    
                    conditions.append([grade, mode, str(courses)])
                    parsed = True
                    break
            
            if not parsed:
                conditions.append(line)
                
                
        
        print()
        print(conditions,"\n\n")
        return str(conditions)
        if "Corequisite(s): " in text:
            text.split("Corequisite(s): ")
        
        
        print(text)
        print()
        
        return [
            ("one of", [])
            
        ]
    
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
        
        