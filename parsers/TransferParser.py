import pdfquery
import os

from schema.Catalogue import Catalogue
from schema.Transfer import Transfers, Transfer
'''
Parses bctransferguide.ca with an ahk script (and much pain)

The process is currently very manual and it's going to be difficult to make 
it more automatic because bctransferguide.ca is very javascript based

For now, paste the output from ahk_data_generator into the ahk script

TODO: some subjects need to be cut in half because the api just can't handle them (cpsc, hist, fina)
'''

class TransferParser:
    
    # 1) navigate to 
    # 2) click on the page
    # 3) open console and paste this in
    # navigator.clipboard.writeText(document.getElementsByClassName("multiselect__content")[2].innerHTML)
    # paste the output into here
    def transfer_courses_generator() -> dict[str, str]:
        
        with open("data/transfer/html.html", "r") as fi:
            html = fi.read()
        
        html = html.split(" - ")
        
        courses: dict[str, str] = {}
        
        for i in range(len(html) - 1):
            subject = html[i].split(">")[-1] # CPSC
            name = html[i+1].split("<")[0].strip()  # Computer Science
            
            courses[subject] = name
        
        return courses
        
    
    
    def ahk_data_generator():
        cat = Catalogue().parse_file("data/catalogue/catalogue.json")

        all_courses:dict[str, list[int]] = {
            
        }
        
        for course in cat.courses:
            if course.subject not in all_courses:
                all_courses[course.subject] = []
            
            all_courses[course.subject].append(course.course_code)
        
        
                
        available_transfers = TransferParser.transfer_courses_generator()
        
        out = ""

        for subject in all_courses:
            
            # don't get transfers if a subject has no transfers
            if subject not in available_transfers:
                continue
            
            
            out += f"{subject} - {available_transfers[subject]}:"
            
            for code in all_courses[subject]:
                out += str(code) + " "
            out = out[:-1] + ","
        
        out = out[:-1] 
           
        print(out)
        
        
        
    def parse_and_save_transfer_pdfs() -> None:
        pdfs = os.listdir("data/transfer/pdf/")
        transfers: Transfers = Transfers()
        
        #pdfs = ["FSRV.pdf"]
        
        for p in pdfs:

            pdf = pdfquery.PDFQuery("data/transfer/pdf/" + p)
            pdf.load()

            # save xml
            #pdf.tree.write("pain.xml", pretty_print=True)

            pyquery = pdf.pq("LTTextBoxHorizontal")

            stuff:list[str] = []

            for i in pyquery.contents():
                
                # for some reason some elements become lxml.etree._ElementUnicodeResult 
                # and others become pdfquery.pdfquery.LayoutElement
                # ???
                # TODO: make this not terrible
                
                
                try:
                    stuff.append(i.text.strip())
                except:    
                    try:
                        stuff.append(str(i).strip())
                    except:
                        print(f"Could not save {i} {type(i)}")
                        
                # don't save empty ones (idk why there are empty ones)
                # WHY DOESNT THIS WORK
                if stuff[-1].isspace():
                    stuff.pop(-1)

            while "" in stuff:
                stuff.remove("")
                    
            '''
            Remove the following:
            Course Search Result from "Course Loads"
            217 agreements found for 15 courses at 17 institutions
            Generated Apr 9, 2023
            1 of 23
            From
            To
            Transfer Credit
            Effective Date
            '''

            '''
            Parsing something like this:
            LANG ABST 1100
            (there may or may not be a 1 or 2 line description here)
            Credits: 3
            Langara College (BC)
            CAPU
            CAPU HIST 209 (3)
            May/03 to
            present (sometimes present is on the same line as above)
            '''
            print(f"Parsing {p} with {stuff[1]}.")
            #print(stuff[0:50])
            
            # sometimes the 1 of 23 pagecount doesn't show up????
            if "of" in stuff[3]:
                stuff = stuff[8:]
            else:
                stuff = stuff[7:]

            i = 0
            while i < len(stuff):
                
                title = stuff[i].split(" ")
                i += 1
                    
                while "Credits:" not in stuff[i]:
                    description = stuff[i]
                    i += 1
                
                # we don't need the # of credits
                # credit = float(stuff[i].split(":")[-1])
                i += 1
                
                i += 1 # skip Langara College (BC)
                
                dest = stuff[i]
                i += 1
                
                
                #print("Getting transfer info:")
                #print(stuff[i])
                transfer = stuff[i]
                i += 1
                
                while stuff[i][6:9] != " to" or (not stuff[i][4:6].isnumeric() and not stuff[i][3] == "/"):
                    #print(stuff[i])

                    transfer += " " + stuff[i]
                    i += 1
                    
                validity = stuff[i].split("to")
                start = validity[0].strip()
                i += 1
                
                
                if len(validity) == 2 and validity[1] != "":
                    end = validity[1].strip()
                else:
                    # if there is a second line
                    end = stuff[i].strip()
                    i += 1
                    
                    
                transfers.courses.append(Transfer(
                    subject = title[1],
                    course_code = title[2],
                    source=title[0],
                    destination=dest, 
                    credit=transfer,
                    effective_start=start,
                    effective_end=end,
                ))
                
                # why is 8 of 23 here??? what about 1-7 of 23???
                # i don't know why only some of the page numbers show up :sob:
                while i < len(stuff) and " of " in stuff[i]:
                    i += 1
                    
                    
                
                
        transfers.saveToFile()
        return Transfers
                
