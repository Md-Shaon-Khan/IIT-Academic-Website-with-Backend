from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from .database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    batch = Column(String(10), index=True)
    project_name = Column(String(255))
    introduction = Column(Text)
    problem_statement = Column(Text)
    features = Column(Text)
    tools_tech = Column(Text)
    impact = Column(Text)
    supervisor = Column(String(100))
    team_members = Column(Text)
    image_path = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class ProjectImage(Base):
    __tablename__ = "project_images"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    image_path = Column(String(255))