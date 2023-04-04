import os

from parser.Parser import Parser
import uvicorn
import schedule


# refresh current semester every 24 hours
def job():
    p = Parser(2023, 20)
    p.loadPageFromWeb()
    p.parseAndSave()
    
    Parser.loadParseSaveAll()


if __name__ == "__main__":
    
    if not os.path.exists("/json"):
        print("No data found. Downloading and parsing all course data.")
        Parser.loadParseSaveAll()
    
    job()
    schedule.every().day.do(job)
    
    uvicorn.run("api.Api:app")
