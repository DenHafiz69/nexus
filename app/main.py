from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import engine, Base
from app import qr_generator, url_shortener, text_converter

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nexus")
templates = Jinja2Templates(directory="templates")

app.include_router(qr_generator.router)
app.include_router(text_converter.router)
app.include_router(url_shortener.router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
