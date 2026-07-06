from app.data.sample_data import TABLE_ROWS
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from app.api.v1.system import router as system_router

app = FastAPI(title="HyperSheet")

# Static dosyalar
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# HTML şablonları
templates = Jinja2Templates(directory="app/templates")

# API
app.include_router(system_router, prefix="/api/v1")


@app.get("/")
async def home(request: Request):
    table_rows =  []

    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={
        "table_rows": TABLE_ROWS
    }
)


@app.get("/health")
def health():
    return JSONResponse(
        {
            "status": "ok",
            "service": "HyperSheet API"
        }
    )
