import string
import random
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import URLItem

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@router.post("/shorten", response_class=HTMLResponse)
async def shorten_url(request: Request, url: str = Form(...), db: Session = Depends(get_db)):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Generate a unique short code
    while True:
        short_code = generate_short_code()
        existing = db.query(URLItem).filter(URLItem.short_code == short_code).first()
        if not existing:
            break

    new_item = URLItem(target_url=url, short_code=short_code)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    short_link = f"{request.base_url}{short_code}"
    return templates.TemplateResponse(
        request=request,
        name="partials/short_link.html", 
        context={"short_link": short_link, "original_url": url}
    )

@router.get("/{short_code}")
async def redirect_url(short_code: str, db: Session = Depends(get_db)):
    item = db.query(URLItem).filter(URLItem.short_code == short_code).first()
    if item:
        return RedirectResponse(url=item.target_url)
    raise HTTPException(status_code=404, detail="URL not found")
