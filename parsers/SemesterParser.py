import requests
from bs4 import BeautifulSoup
import unicodedata
import os
import datetime

from schema.Semester import Course, Semester, ScheduleEntry, RPEnum, seatsEnum, waitlistEnum


'''
Parses the Langara Course Search into json

this classname is very deceptive: This class has methods for
- fetching course pages from the internet
- downloading course pages
- parsing course page

TODO: speed it up - it takes 3 mins to download and parse all 20 years of data :sob:
'''

class SemesterParser:
    def __init__(self, year:int, semester:int) -> None:
        
        if year < 2000:
            raise Exception("Course data is not available prior to 2000.")
        if semester not in [10, 20, 30]:
            raise Exception(f"Invalid semester {semester}. Semester must be 10, 20 or 30.")
        
        self.year = year 
        self.semester = semester
        
        self.page: str = None
        self.courses_first_day = None
        self.courses_last_day = None    # last day of classes - does not include final exam period
        
        self.save_location = "data"
    
    # Tries to load page from file system
    # TODO: if we ever speed up the parsing put a ratelimit on this
    def loadPageFromFile(self) -> None:
        file_location = f"{self.save_location}/pages/{self.year}{self.semester}.html"
        
        with open(file_location, "r") as p:
            self.page = p.read()
                
    # Tries to get page from website
    def loadPageFromWeb(self, saveHTML:bool = True) -> None:
        self.page = self.getPageFromWeb(self.year, self.semester)
        
        if saveHTML:
            self.savePage()
    
    # Tries to load page from file, then tries to access it on the internet
    def loadPage(self, getPageFromWeb:bool = False, saveHTML:bool = True) -> None:
        
        if getPageFromWeb:
            print(f"Downloading {self.year}{self.semester} from langara.ca.")
            self.loadPageFromWeb(saveHTML)
            print(f"Download complete.")
            return
        
        try:
            self.loadPageFromFile()
            print(f"Loaded {self.year}{self.semester} from {self.save_location}/pages/.")
        except:
            print(f"Downloading {self.year}{self.semester} from langara.ca because no local copy was found.")
            self.loadPageFromWeb(saveHTML)
            print(f"Download complete.")
    
    # Loads and parses ALL pages 
    def loadParseSaveAll(getPagesFromWeb:bool = False) -> None:
        for year in range(2000, 2023):
            for semester in range(10, 31, 10):
                
                p = SemesterParser(year, semester)
                p.loadPage(getPageFromWeb=getPagesFromWeb)
                
                s = p.parseAndSave()
                print(s)
                
    # Returns raw html of a course search for a given semester
    def getPageFromWeb(self, year:int, semester:int) -> str:
        
        # get available subjects (ie ABST, ANTH, APPL, etc)
        url = f"https://swing.langara.bc.ca/prod/hzgkfcls.P_Sel_Crse_Search?term={year}{semester}"
        i = requests.post(url)
        
        # TODO: optimize finding this list
        soup = BeautifulSoup(i.text, "lxml")
        courses = soup.find("select", {"id":"subj_id"})
        courses = courses.findChildren()
        subjects = []
        for c in courses: # c = ['<option value=', 'SPAN', '>Spanish</option>']
            subjects.append(str(c).split('"')[1])

        #print("Available subjects: ", subjects)
        
        subjects_data = ""
        for s in subjects:
            subjects_data += f"&sel_subj={s}"

        url = "https://swing.langara.bc.ca/prod/hzgkfcls.P_GetCrse"
        headers = {'Content-type': 'application/x-www-form-urlencoded'}

        data = f"term_in={year}{semester}&sel_subj=dummy&sel_day=dummy&sel_schd=dummy&sel_insm=dummy&sel_camp=dummy&sel_levl=dummy&sel_sess=dummy&sel_instr=dummy&sel_ptrm=dummy&sel_attr=dummy&sel_dept=dummy{subjects_data}&sel_crse=&sel_title=%25&sel_dept=%25&begin_hh=0&begin_mi=0&begin_ap=a&end_hh=0&end_mi=0&end_ap=a&sel_incl_restr=Y&sel_incl_preq=Y&SUB_BTN=Get+Courses"
        i = requests.post(url, headers=headers, data=data)
        
        return i.text
    
    # saves a page to file
    def savePage(self) -> None:
            
        if self.page == "":
            raise Exception("Cannot save empty page.")
        
        path = f"{self.save_location}/pages/{self.year}{self.semester}.html"
        # create dir if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, "w+") as fi:
            fi.write(self.page)
            
    # parses self.page and saves the parsed result
    def parseAndSave(self) -> Semester:
        s = self.parse()
        s.saveToFile(location=self.save_location)
        return s
        
    """
    Parses a page and returns all of the information contained therein.
    
    Naturally there are a few caveats"
    1) If they ever change the course search interface, this will break horribly
    2) For a few years, they had a course-code note that applied to all sections of a course.
       Instead of storing that properly, we simply append that note to the end of all sections of a course.
    
    """
    # TODO: refactor this method to make it quicker
    def parse(self) -> Semester:
        semester = Semester(year=self.year, semester=self.semester)
                
        # use BeautifulSoup to change html to Python friendly format
        soup = BeautifulSoup(self.page, 'lxml')

        # "the Course Search For Spring 2023" is the only h2 on the page
        # confirm that term is as expected
        title = soup.find("h2").text.split()

        year = int(title[-1])
        match title[-2]:
            case "Spring":
                term = 10
            case "Summer":
                term = 20
            case "Fall":
                term = 30
                
        if year != self.year or term != self.semester:
            raise Exception(f"Year/semester different than specified: {year}{term}. Expected {self.year}{self.semester}.")

        # get the table with all the courses
        table1 = soup.find("table", class_="dataentrytable")


        # write each entry on the table into a list
        # do not save anything we do not need (headers, lines and courrse headings)
        rawdata:list[str] = []
        for i in table1.find_all("td"):
            
            # remove the grey separator lines
            if "deseparator" in i["class"]: 
                continue
            
            # if a comment is >2 lines, theres whitespace added underneath, this removes them
            if "colspan" in i.attrs and i.attrs["colspan"] == "22":
                continue
            
            # fix unicode encoding
            txt = unicodedata.normalize("NFKD", i.text)
            
            # remove the yellow headers
            if txt == "Instructor(s)":
                rawdata = rawdata[0:-18]
                continue
            
            # remove the header for each course (e.g. CPSC 1150)
            if (len(txt) == 9 and txt[0:4].isalpha() and txt[5:9].isnumeric()):
                continue
            
            # remove non standard header (e.g. BINF 4225 ***NEW COURSE***)
            # TODO: maybe add this to notes at some point?
            if txt[-3:] == "***":
                continue
            
            rawdata.append(txt)

        i = 0
        sectionNotes = None

        while i < len(rawdata)-1:
            
            # some class-wide notes that apply to all sections of a course are put in front of the course (see 10439 in 201110)
            # this is a bad way to deal with them
            if len(rawdata[i]) > 2:
                # 0 stores the subj and course id (ie CPSC 1150)
                # 1 stores the note and edits it properly
                sectionNotes = [
                    rawdata[i][0:9],
                    rawdata[i][10:].strip()
                ]
                #print("NEW SECTIONNOTES:", sectionNotes)
                i += 1
                
            # terrible way to fix off by one error (see 30566 in 201530)
            if rawdata[i].isdigit():
                i -= 1
            
            fee:str = formatProp(rawdata[i+10])
            # required to convert "$5,933.55" -> 5933.55
            if fee != None:
                fee = fee.replace("$", "")
                fee = fee.replace(",", "")
                fee = float(fee)
            
            rpt = formatProp(rawdata[i+11])
            if rpt == "-":
                rpt = None  
                        
            current_course = Course(
                RP          = formatProp(rawdata[i]),
                seats       = formatProp(rawdata[i+1]),
                waitlist    = formatProp(rawdata[i+2]),
                # skip the select column
                crn         = formatProp(rawdata[i+4]),
                subject     = rawdata[i+5],
                course_code = formatProp(rawdata[i+6]),
                section     = rawdata[i+7],
                credits     = formatProp(rawdata[i+8]),
                title       = rawdata[i+9],
                add_fees    = fee,
                rpt_limit   = rpt,
                
                notes = None,
                schedule = [],
                
            )
            
            if sectionNotes != None:
                if sectionNotes[0] == f"{current_course.subject} {current_course.course_code}":
                    
                    current_course.notes = sectionNotes[1]
                else:
                    sectionNotes = None
                            
            semester.addCourse(current_course)
            i += 12
            
            while True:
                
                # sanity check
                if rawdata[i] not in [" ", "CO-OP(on site work experience)", "Lecture", "Lab", "Seminar", "Practicum","WWW", "On Site Work", "Exchange-International", "Tutorial", "Exam", "Field School", "Flexible Assessment", "GIS Guided Independent Study"]:
                    raise Exception(f"Parsing error: unexpected course type found: {rawdata[i]}. {current_course} in course {current_course.toJSON()}")
                                        
                c = ScheduleEntry(
                    type       = rawdata[i],
                    days       = rawdata[i+1],
                    time       = rawdata[i+2], 
                    start      = formatDate(rawdata[i+3]), 
                    end        = formatDate(rawdata[i+4]), 
                    room       = rawdata[i+5], 
                    instructor = rawdata[i+6], 
                )
                if c.start.isspace():
                    c.start = self.courses_first_day
                if c.end.isspace():
                    c.end = self.courses_last_day
                
                current_course.schedule.append(c)
                i += 7
                
                # if last item in courselist has no note return
                if i > len(rawdata)-1:
                    break
                                
                # look for next item
                j = 0
                while rawdata[i].strip() == "":
                    i += 1
                    j += 1

                # if j less than 5 its another section
                if j <= 5:
                    i -= j 
                    break
                
                # if j is 9, its a note e.g. "This section has 2 hours as a WWW component"
                if j == 9:
                    # some courses have a section note and a normal note
                    if current_course.notes == None:
                        current_course.notes = rawdata[i].replace("\n", "").replace("\r", "") # dont save newlines
                    else:
                        current_course.notes = rawdata[i].replace("\n", "").replace("\r", "") + "\n" + current_course.notes
                    i += 5
                    break
                
                # otherwise, its the same section but a second time
                if j == 12:
                    continue
                
                else:
                    break
        
        semester.extractDates()
        return semester

# formats inputs for course entries
# this should be turned into a lambda
def formatProp(s:str) -> str | int | float:
        if s.isdecimal():
            return int(s)
        if s.isspace():
            return None
        else:
            return s.strip()


# converts date from "11-Apr-23" to "2023-04-11" (ISO 8601)
def formatDate(date:str) -> datetime.date:
    if date == None:
        return None
    
    if len(date) != 9 or len(date.split("-")) != 3 or date.split("-")[1].isdigit():
        return date
        
    date = date.split("-")
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    
    month = months.index(date[1].lower())+1
    if month <= 9:
        month = "0" + str(month)
    
    out = f"20{date[2]}-{month}-{date[0]}"
    return out
    