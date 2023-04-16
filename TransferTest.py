from openpyxl import LXML
from pydantic import BaseModel
from parsers.TransferParser import TransferParser


#TransferParser.transfer_courses_generator()
#TransferParser.ahk_data_generator()
#TransferParser.parse_and_save_transfer_pdfs()

from builders.CourseInfoBuilder import CourseInfoBuilder

from builders.AllBuilder import AllBuilder

c = AllBuilder()
c.hydrateBuildSave()


print("Done!")