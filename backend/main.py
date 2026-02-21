from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import shutil, os, uuid
from . import models, database

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=database.engine)

if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.post("/upload-project/")
async def upload_project(
    batch: str = Form(...), name: str = Form(...), intro: str = Form(...),
    problem: str = Form(...), features: str = Form(...), tools: str = Form(...),
    impact: str = Form(...), supervisor: str = Form(...), team: str = Form(...),
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
            batch=batch, project_name=name, introduction=intro,
            problem_statement=problem, features=features, tools_tech=tools,
            impact=impact, supervisor=supervisor, team_members=team,
            image_path=cover_path
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

@app.get("/get-project-detail/{project_id}")
def get_detail(project_id: int, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    images = db.query(models.ProjectImage).filter(models.ProjectImage.project_id == project_id).all()
    if not project: raise HTTPException(status_code=404, detail="Not found")
    return {"project": project, "related_images": images}