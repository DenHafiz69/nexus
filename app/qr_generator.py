import io
import base64
import qrcode
from datetime import datetime
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/generate-qr", response_class=HTMLResponse)
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
