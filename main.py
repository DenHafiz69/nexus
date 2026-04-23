import string
import random
import io
import base64
import qrcode
from datetime import datetime
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import URLItem

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nexus")
templates = Jinja2Templates(directory="templates")

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/shorten", response_class=HTMLResponse)
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

@app.get("/{short_code}")
async def redirect_url(short_code: str, db: Session = Depends(get_db)):
    item = db.query(URLItem).filter(URLItem.short_code == short_code).first()
    if item:
        return RedirectResponse(url=item.target_url)
    raise HTTPException(status_code=404, detail="URL not found")

@app.post("/generate-qr", response_class=HTMLResponse)
async def generate_qr(request: Request, text: str = Form(...)):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save the image to an in-memory byte buffer
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    # Encode as base64 string to embed directly in HTML
    img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    
    # Generate timestamp-based filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"qr-{timestamp}.png"
    
    return templates.TemplateResponse(
        request=request,
        name="partials/qr_code.html", 
        context={
            "qr_data_uri": f"data:image/png;base64,{img_b64}", 
            "text": text,
            "filename": filename
        }
    )
