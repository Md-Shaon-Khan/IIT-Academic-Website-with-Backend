from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import or_ 
import shutil, os, uuid
import models, database

from database import SessionLocal, engine, get_db
from auth import verify_password, create_token, hash_password
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from auth import SECRET_KEY, ALGORITHM
from mailer import send_otp_email
from datetime import datetime, timedelta
import secrets

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5502", "http://localhost:5502"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=database.engine)

if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


security = HTTPBearer()

def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=403, detail="Invalid or expired token")


@app.post("/upload-project/")
async def upload_project(
    batch: str = Form(...),
    course_id: int = Form(...),         # renamed from course -> course_id
    name: str = Form(...), 
    intro: str = Form(...),
    problem: str = Form(...), 
    features: str = Form(...), 
    tools: str = Form(...),
    impact: str = Form(...), 
    supervisor: str = Form(...), 
    team: str = Form(...),
    github_link: str = Form(None),
    image: UploadFile = File(...), 
    related_images: list[UploadFile] = File(None), 
    db: Session = Depends(database.get_db)
):
    try:
        ext = image.filename.split(".")[-1]
        unique_cover = f"{uuid.uuid4()}.{ext}"
        cover_path = f"uploads/{unique_cover}"
        with open(cover_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        new_project = models.Project(
            batch=batch,
            course_id=course_id,        # renamed from course -> course_id
            project_name=name, 
            introduction=intro,
            problem_statement=problem, 
            features=features, 
            tools_tech=tools,
            impact=impact, 
            supervisor=supervisor, 
            team_members=team,
            image_path=cover_path,
            github_link=github_link
        )
        db.add(new_project)
        db.flush()

        if related_images:
            for img in related_images:
                if img.filename:
                    img_ext = img.filename.split(".")[-1]
                    img_name = f"{uuid.uuid4()}.{img_ext}"
                    img_path = f"uploads/{img_name}"
                    with open(img_path, "wb") as buffer:
                        shutil.copyfileobj(img.file, buffer)
                    db.add(models.ProjectImage(project_id=new_project.id, image_path=img_path))

        db.commit()
        return {"status": "success", "message": "Project uploaded successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get-projects/{batch_id}")
def get_projects(batch_id: str, db: Session = Depends(database.get_db)):
    return db.query(models.Project).filter(models.Project.batch == batch_id).all()


@app.get("/search-projects/")
def search_projects(query: str, db: Session = Depends(database.get_db)):
    search_query = f"%{query}%"
    results = db.query(models.Project).filter(
        or_(
            models.Project.project_name.ilike(search_query),
            models.Project.introduction.ilike(search_query),
            models.Project.batch.ilike(search_query),
            # course_id removed — integer columns don't support ilike
        )
    ).all()
    return results


@app.get("/get-project-detail/{project_id}")
def get_detail(project_id: int, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    images = db.query(models.ProjectImage).filter(models.ProjectImage.project_id == project_id).all()
    if not project:
        raise HTTPException(status_code=404, detail="Not found")
    return {"project": project, "related_images": images}


@app.delete("/delete-project/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        images = db.query(models.ProjectImage).filter(models.ProjectImage.project_id == project_id).all()
        for img in images:
            if os.path.exists(img.image_path):
                os.remove(img.image_path)
        if os.path.exists(project.image_path):
            os.remove(project.image_path)
        db.query(models.ProjectImage).filter(models.ProjectImage.project_id == project_id).delete()
        db.delete(project)
        db.commit()
        return {"status": "success", "message": "Project deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/request-otp")
def request_otp(email: str = Form(...), db: Session = Depends(get_db)):
    allowed = db.query(models.AllowedEmail).filter(
        models.AllowedEmail.email == email,
        models.AllowedEmail.is_registered == False
    ).first()
    if not allowed:
        raise HTTPException(status_code=403, detail="This email is not authorized or already has an account.")

    otp = str(secrets.randbelow(900000) + 100000)
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    try:
        send_otp_email(email, otp)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")

    db.query(models.EmailOTP).filter(models.EmailOTP.email == email).delete()
    db.add(models.EmailOTP(email=email, otp=otp, expires_at=expires_at))
    db.commit()
    return {"message": "OTP sent to your email."}


@app.post("/auth/signup")
def signup(
    email: str = Form(...),
    otp: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    otp_record = db.query(models.EmailOTP).filter(
        models.EmailOTP.email == email,
        models.EmailOTP.otp == otp,
        models.EmailOTP.used == False,
        models.EmailOTP.expires_at > datetime.utcnow()
    ).first()
    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")

    hashed = hash_password(password)
    new_admin = models.Admin(username=username, email=email, password=hashed)
    db.add(new_admin)
    otp_record.used = True
    db.query(models.AllowedEmail).filter(
        models.AllowedEmail.email == email
    ).update({"is_registered": True})
    db.commit()
    return {"message": "Account created successfully! You can now log in."}


@app.post("/admin/allow-email")
def allow_email(
    email: str = Form(...),
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin)
):
    existing = db.query(models.AllowedEmail).filter(
        models.AllowedEmail.email == email
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already in the list.")
    db.add(models.AllowedEmail(email=email))
    db.commit()
    return {"message": f"{email} added to allowed list."}


@app.post("/admin/create")
def create_admin(username: str = Form(...),
                 email: str = Form(...),
                 password: str = Form(...),
                 db: Session = Depends(get_db)):
    hashed = hash_password(password)
    admin = models.Admin(username=username, email=email, password=hashed)
    db.add(admin)
    db.commit()
    return {"message": "Admin created"}


@app.post("/admin/login")
def admin_login(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    admin = db.query(models.Admin).filter(
        models.Admin.email == email,
        models.Admin.username == username
    ).first()
    if not admin:
        raise HTTPException(status_code=400, detail="Admin not found")
    if not verify_password(password, admin.password):
        raise HTTPException(status_code=400, detail="Wrong password")
    token = create_token({"sub": admin.email, "username": admin.username})
    return {"message": "Login successful", "access_token": token}