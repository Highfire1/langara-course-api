from pydantic import BaseModel, Field
from enum import Enum

from schema.Semester import RPEnum

class institutions(Enum):
    SFU = "SFU"
    UBCV = "UBCV"


class TransferInfo(BaseModel):
    institution: 'institutions' = Field(description='Institution this transfer credit is for.')
    credit: str                 = Field(description='How the credit transfers e.g.  SFU CMPT 1XX (3), Q/B-Sci.')
    effective_date: str         = Field(description="Effective Date e.g. Sep/99 ongoing.")

    class Config:
        schema_extra = {
            "example": {
                "institution" : institutions.SFU,
                "credit" : "SFU CMPT 1XX (3), Q/B-Sci",
                "effective_date" : "Sep/99 ongoing"
            },
            "example2": {
                "institution" : institutions.UBCV,
                "credit" : " UBCV CPSC 101 (4)",
                "effective_date" : "Sep/08 ongoing"
            }
        }

class Prerequisite(BaseModel):
    pass

    
class availability(Enum):
    spring = "spring"
    summer = "summer"
    fall = "fall"
    springsummer = "springsummer"
    springfall = "springfall"
    summerfall = "summerfall"
    all = "all"
    unknown = "unknown"
    
class attributes(Enum):
    AR =  "2AR"
    SC = "2SC"
    HUM = "HUM"
    LSC = "LSC"
    SCI = "SCI"
    SOC = "SOC"
    UT = "UT"
    


class CourseInfo(BaseModel):
    RP : 'RPEnum'           = Field(description='Prerequisites of the course.')
    subject: str        = Field(description="Subject area e.g. ```CPSC```.")
    course_code: int    = Field(description="Course code e.g. ```1050```.")     
    credits: float      = Field(description="Credits the course is worth.")
    title: str          = Field(description="*Unabbreviated* title of the course e.g. ```Intro to Computer Science```.")
    description: str    = Field(description="Description of course.")
    add_fees: float     = Field(description="Additional fees (in dollars).")
    rpt_limit: int      = Field(description="Repeat limit. ```0``` means there is no repeat limit.")
    availability: 'availability'            = Field(description="Availability of course. Extracted automatically - may not be correct. Consult langara advisors if in doubt.")
    last_offered : list[int]                = Field(description="last 5 semesters the course was offered e.g. ```[202310, 202210, 202010, 201910, 201810]```. Note that cancelled sections are included.")
    # how do i get this to show on docs???
    attributes : dict['attributes', bool]   = Field(description="Langara attributes for a course.")
    transfer: list[TransferInfo] | None     = Field(description="Information on how the course transfers. Only supports UBC & SFU.")
    prerequisites: list[Prerequisite] | None= Field(description="Prerequisites for the course. Accuracy not guaranteed")
    restriction: str | None                 = Field(description="Program you must be in to register for this course")
    
    class Config:
        schema_extra = {
            "example": {
                "RP" : None,
                "subject" : "CPSC",
                "course_code" : 1000,
                "credits" : 3.0,
                "title": "Introduction to Computer Science",
                "description" : "Offers a broad overview of the computer science discipline. Provides students with an appreciation for and an understanding of the many different aspects of the discipline. Topics include information and data representation; introduction to computer hardware and programming; networks; applications (e.g., spreadsheet, database); social networking; ethics; and history. Intended for both students expecting to continue in computer science as well as for those taking it for general interest.",
                "add_fees" : 34.00,
                "rpt_limit" : 2,
                "availability" : availability.all,
                "last_offered" : [202320, 202310, 202230, 202220, 202210],
                "attributes" : {
                    "2AR" : False,
                    "2SC" : False,
                    "HUM" : False,
                    "LSC" : False,
                    "SCI" : True,
                    "SOC" : False,
                    "UT" :  True,
                },
                "transfer" : [
                    TransferInfo.Config.schema_extra["example"],
                    TransferInfo.Config.schema_extra["example2"]
                    ],
            }
        }
