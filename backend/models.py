from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from datetime import datetime
from database import Base


class Course(Base):
    __tablename__ = "course"
    course_id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String(100))


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    batch = Column(String(10), index=True)
    course_id = Column(Integer, ForeignKey("course.course_id"), index=True)
    project_name = Column(String(255))
    introduction = Column(Text)
    problem_statement = Column(Text)
    features = Column(Text)
    tools_tech = Column(Text)
    impact = Column(Text)
    supervisor = Column(String(100))
    team_members = Column(Text)
    image_path = Column(String(255))
    github_link = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ProjectImage(Base):
    __tablename__ = "project_images"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    image_path = Column(String(255))


class AllowedEmail(Base):
    __tablename__ = "allowed_emails"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    is_registered = Column(Boolean, default=False)


class EmailOTP(Base):
    __tablename__ = "email_otps"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    otp = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)


class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True)
    email = Column(String(150), unique=True)
    password = Column(String(255))