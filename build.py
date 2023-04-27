import sys


from builders.AllBuilder import AllBuilder
from builders.CourseInfoBuilder import CourseInfoBuilder
from parsers.CatalogueParser import CatalogueParser
from parsers.SemesterParser import SemesterParser
from parsers.TransferParser import TransferParser
from parsers.AttributesParser import AttributesParser


"""
Parse all data.
May fetch content from the internet if not found in data/
May take some time.
"""
def parse_build_data(getFromWeb = False):
    SemesterParser.loadParseSaveAll(getPagesFromWeb=getFromWeb)

    p = AttributesParser()
    p.LoadParseAndSave(getPageFromWeb=getFromWeb)
    
    c = CatalogueParser()
    c.LoadParseAndSave(getPageFromWeb=getFromWeb)
    
    # The process for fetching transfer data is currently
    # very manual and is not automated.
    
    #TransferParser.transfer_courses_generator()
    #TransferParser.ahk_data_generator()
    TransferParser.parse_and_save_transfer_pdfs()
    
    
    c = CourseInfoBuilder()
    c.hydrateBuildSave()
    
    a = AllBuilder()
    a.hydrateBuildSave()

def UPDATE_ALL(getFromWeb = False): 
    p = SemesterParser(2023, 20)
    p.loadPageFromWeb()
    p.parseAndSave()

    parse_build_data(getFromWeb=getFromWeb)
    sys.exit()
    
# WARNING: this takes 9 minutes and 30 seconds to finish on my laptop
# DOUBLE WARNING: this takes 18 minutes if you download new data
# TODO: make this faster (?)
UPDATE_ALL(getFromWeb=False) 