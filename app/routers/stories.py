from typing import List, Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..import models, schemas, oauth2
from ..database import get_db


router = APIRouter(
    prefix="/story",
    tags=['Story']
)

# mengambil semua data
@router.get("/", response_model=List[schemas.StoryOut])
def get_stories(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):


    stories = db.query(models.Story, func.count(models.Likes.story_id).label("likes")).join(models.Likes, models.Likes.story_id == models.Story.id, isouter=True).group_by(models.Story.id).filter(models.Story.title.contains(search)).limit(limit).offset(skip).all()

    return stories


# membuat data
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Story)
def create_stories(story: schemas.StoryCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    new_story = models.Story(owner_id=current_user.id, **story.dict())
    db.add(new_story)
    db.commit()
    db.refresh(new_story)
    return new_story

# mengambil data berdasarkan id
@router.get("/{id}", response_model=schemas.StoryOut)
def get_story(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):


    story = db.query(models.Story, func.count(models.Likes.story_id).label("likes")).join(models.Likes, models.Likes.story_id == models.Story.id, isouter=True).group_by(models.Story.id).filter(models.Story.id == id).first()
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"story with id: {id} was not found")
    return story

# menghapus cerita
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_story(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    story_query = db.query(models.Story).filter(models.Story.id == id)
    story = story_query.first()
    if story == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"story with id: {id} does not exist")
    
    if story.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    story_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# update
@router.put("/{id}", response_model=schemas.Story)
def update_story(id: int, updated_post: schemas.StoryCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    story_query = db.query(models.Story).filter(models.Story.id == id)
    story = story_query.first()

    if story == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"story with id: {id} does not exist")
    
    if story.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    story_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return story_query.first()