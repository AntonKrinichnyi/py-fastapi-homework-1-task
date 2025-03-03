from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.movies import MovieDetailReponseSchema, MovieListResponseSchema
from database import get_db, MovieModel


router = APIRouter()

@router.get("/movies/{movie_id}/", response_model=MovieDetailReponseSchema)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MovieModel).where(MovieModel.id == movie_id))
    movie = result.scalar_one_or_none()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@router.get("/movies/", response_model=MovieListResponseSchema)
async def get_movies(page: int = 1, per_page: int = 5, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MovieModel))
    movies = result.scalars().all()
    total_items = len(movies)
    total_pages = total_items // per_page
    prev_page = f"/movies/?page={page-1}&per_page={per_page}" if page > 1 else None
    next_page = f"/movies/?page={page+1}&per_page={per_page}" if page < total_pages else None
    if page > total_pages:
        raise HTTPException(status_code=404, detail="Page not found")
    movies = movies[(page-1)*per_page:page*per_page]
    return {
        "movies": movies,
        "prev_page": prev_page,
        "next_page": next_page,
        "total_pages": total_pages,
        "total_items": total_items
    }
