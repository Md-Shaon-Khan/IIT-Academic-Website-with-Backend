from pydantic import BaseModel

class Final_question(BaseModel):
    course_id:int
    batch:int
    content:str
    