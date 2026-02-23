from pydantic import BaseModel

class Project(BaseModel):
    batch:int
    course_id:int
    title:str
    description:str
    feature:str
    tools:str
    supervisor:int
    githublink:str
    reportlink:str
    image:str
    