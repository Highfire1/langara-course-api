import sys
from builders.AllBuilder import AllBuilder
from builders.CourseInfoBuilder import CourseInfoBuilder
from schema.Semester import Semester
from parsers.SemesterParser import SemesterParser

year = 2023
semester = 20

modes = [
    f"Refetch and parse {year}{semester}.",
    f"Reparse {year}{semester}.",
    "Reparse all semesters.",
    "Refetch and parse all semesters."
]


a = CourseInfoBuilder()
a.hydrateBuildSave()

sys.exit()

print("Select a mode:")
for i, mode in enumerate(modes):
    print(f"({i+1}) {mode}")

mode = input("Selection: ")



if mode == "1":
    p = SemesterParser(year, semester)
    p.loadPageFromWeb()
    p.parseAndSave()

if mode == "2":
    s = Semester.parse_file(f"data/json/{year}{semester}.json")
    print(s)

if mode == "3":
    SemesterParser.loadParseSaveAll()

if mode == "4":
    SemesterParser.loadParseSaveAll(getPagesFromWeb=True)
   
   
   

print("Done!")