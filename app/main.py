from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

# Create database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Nexus URL Shortener",
    description="A simple and fast URL shortener API.",
    version="1.0.0",
)

# Dependency to get a database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/shorten", response_model=schemas.URLInfo, status_code=201)
def create_short_url(
    request: Request, url: schemas.URLCreate, db: Session = Depends(get_db)
):
    """
    Creates a short link for a given original URL.

    - **original_url**: The URL to shorten.
    """
    db_url = crud.create_db_url(db=db, url=url)

    # Construct the full shortened URL using the request's base URL
    base_url = str(request.base_url)
    shortened_url = f"{base_url}{db_url.short_code}"

    return schemas.URLInfo(
        original_url=db_url.original_url, shortened_url=shortened_url
    )


@app.get("/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    """
    Redirects a short code to its original URL and tracks the click.
    """
    db_url = crud.get_url_by_short_code(db, short_code=short_code)
    if db_url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # Increment the click count
    crud.update_clicks(db=db, db_url=db_url)

    return RedirectResponse(url=db_url.original_url)