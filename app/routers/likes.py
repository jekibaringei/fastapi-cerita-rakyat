from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import schemas, database, models, oauth2



router = APIRouter(
    prefix="/likes",
    tags=["Likes"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def like(like: schemas.Likes, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):

    story = db.query(models.Story).filter(models.Story.id == like.story_id).first()
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"story with id: {like.story_id} does not exist")
    
    like_query = db.query(models.Likes).filter(models.Likes.story_id == like.story_id, models.Likes.user_id == current_user.id)
    found_like = like_query.first()
    if (like.dir == 1):
        if found_like:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user {current_user.id} has already vote on post {like.story_id}")
        new_like = models.Likes(story_id = like.story_id, user_id = current_user.id)
        db.add(new_like)
        db.commit()
        return {"message": "successfully added vote"}
    else:
        if not found_like:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Like does not exist")
        like_query.delete(synchronize_session=False)
        db.commit()

        return {"message": "successfully deleted like"}