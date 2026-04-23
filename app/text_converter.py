import re
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def to_camel_case(text: str) -> str:
    s = re.sub(r"(_|-)+", " ", text).title().replace(" ", "")
    return ''.join([s[0].lower(), s[1:]]) if s else ""

def to_snake_case(text: str) -> str:
    s = re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()
    return re.sub(r"[\s\-]+", "_", s)

def to_kebab_case(text: str) -> str:
    s = re.sub(r'(?<!^)(?=[A-Z])', '-', text).lower()
    return re.sub(r"[\s_]+", "-", s)

def to_alternating_case(text: str) -> str:
    result = []
    upper = True
    for char in text:
        if char.isalpha():
            result.append(char.upper() if upper else char.lower())
            upper = not upper
        else:
            result.append(char)
    return "".join(result)

@router.get("/text-converter", response_class=HTMLResponse)
async def text_converter_page(request: Request):
    return templates.TemplateResponse(request=request, name="text_converter.html")

@router.post("/convert-text", response_class=HTMLResponse)
async def convert_text(request: Request, text: str = Form(...), case_type: str = Form(...)):
    converted_text = text
    
    if case_type == "uppercase":
        converted_text = text.upper()
    elif case_type == "lowercase":
        converted_text = text.lower()
    elif case_type == "titlecase":
        converted_text = text.title()
    elif case_type == "camelcase":
        converted_text = to_camel_case(text)
    elif case_type == "snakecase":
        converted_text = to_snake_case(text)
    elif case_type == "kebabcase":
        converted_text = to_kebab_case(text)
    elif case_type == "alternatingcase":
        converted_text = to_alternating_case(text)
        
    return templates.TemplateResponse(
        request=request,
        name="partials/text_result.html", 
        context={
            "converted_text": converted_text,
            "original_text": text
        }
    )
