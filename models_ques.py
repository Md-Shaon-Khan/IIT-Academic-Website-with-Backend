from pydantic import BaseModel

class Tutorial_question(BaseModel):
    tutorial_number:int
    course_id:int
    batch:int
    content:str
    