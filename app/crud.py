import secrets
from sqlalchemy.orm import Session

from . import models, schemas


def get_url_by_short_code(db: Session, short_code: str) -> models.URL | None:
    """
    Retrieve a URL from the database by its short code.
    """
    return db.query(models.URL).filter(models.URL.short_code == short_code).first()


def get_url_by_original_url(db: Session, original_url: str) -> models.URL | None:
    """
    Retrieve a URL from the database by its original URL.
    """
    return db.query(models.URL).filter(models.URL.original_url == original_url).first()


def create_db_url(db: Session, url: schemas.URLCreate) -> models.URL:
    """
    Create a new short URL in the database.
    If the original URL already exists, return the existing entry.
    Otherwise, generate a new unique short code and create a new entry.
    """
    # Check if the URL has already been shortened
    db_url = get_url_by_original_url(db, str(url.original_url))
    if db_url:
        return db_url

    # Generate a unique short code
    while True:
        # Using 5 bytes for a ~7 character URL-safe string
        short_code = secrets.token_urlsafe(5)
        if not get_url_by_short_code(db, short_code):
            break

    db_url = models.URL(original_url=str(url.original_url), short_code=short_code)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


def update_clicks(db: Session, db_url: models.URL) -> models.URL:
    """
    Increment the click count for a given URL.
    """
    db_url.clicks += 1
    db.commit()
    db.refresh(db_url)
    return db_url