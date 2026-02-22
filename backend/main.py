from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import or_ 
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

# --- ENDPOINTS ---

@app.post("/upload-project/")
async def upload_project(
    batch: str = Form(...), 
    name: str = Form(...), 
    intro: str = Form(...),
    problem: str = Form(...), 
    features: str = Form(...), 
    tools: str = Form(...),
    impact: str = Form(...), 
    supervisor: str = Form(...), 
    team: str = Form(...),
    github_link: str = Form(None), # New Field Added
    image: UploadFile = File(...), 
    related_images: list[UploadFile] = File(None), 
    db: Session = Depends(database.get_db)
):
    try:
        # Save Cover Image
        ext = image.filename.split(".")[-1]
        unique_cover = f"{uuid.uuid4()}.{ext}"
        cover_path = f"uploads/{unique_cover}"
        with open(cover_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Create Project Record
        new_project = models.Project(
            batch=batch, 
            project_name=name, 
            introduction=intro,
            problem_statement=problem, 
            features=features, 
            tools_tech=tools,
            impact=impact, 
            supervisor=supervisor, 
            team_members=team,
            image_path=cover_path,
            github_link=github_link # Saved to DB
        )
        db.add(new_project)
        db.flush() 

        # Save Gallery Images
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
            models.Project.batch.ilike(search_query) 
        )
    ).all()
    return results

@app.get("/get-project-detail/{project_id}")
def get_detail(project_id: int, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    images = db.query(models.ProjectImage).filter(models.ProjectImage.project_id == project_id).all()
    if not project: raise HTTPException(status_code=404, detail="Not found")
    return {"project": project, "related_images": images}

@app.delete("/delete-project/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        # Delete related images from disk
        images = db.query(models.ProjectImage).filter(models.ProjectImage.project_id == project_id).all()
        for img in images:
            if os.path.exists(img.image_path):
                os.remove(img.image_path)
        
        # Delete cover image from disk
        if os.path.exists(project.image_path):
            os.remove(project.image_path)

        # Delete from DB
        db.query(models.ProjectImage).filter(models.ProjectImage.project_id == project_id).delete()
        db.delete(project)
        db.commit()
        
        return {"status": "success", "message": "Project deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))