from app.data.sample_data import TABLE_ROWS

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder

from app.api.v1.system import router as system_router
from app.api.v1.excel import router as excel_router


app = FastAPI(title="HyperSheet")

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# HTML templates
templates = Jinja2Templates(directory="app/templates")

# API routers
app.include_router(system_router, prefix="/api/v1")
app.include_router(excel_router, prefix="/api/v1")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "table_rows": TABLE_ROWS
        }
    )


# ---------------------------------------------------------
# Market Network
# ---------------------------------------------------------

@app.get("/market-network")
async def market_network(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="market_network.html",
        context={}
    )


@app.get("/health")
def health():
    return JSONResponse(
        {
            "status": "ok",
            "service": "HyperSheet API"
        }
    )


@app.get("/api/demo/model")
def demo_model():
    from app.db.session import SessionLocal
    from sqlalchemy import text

    db = SessionLocal()

    try:
        datasets = db.execute(text("""
            SELECT id, name, description, source_type, status
            FROM datasets
            WHERE is_deleted = false
            ORDER BY created_at
        """)).mappings().all()

        dimensions = db.execute(text("""
            SELECT id, dataset_id, name, display_name, data_type, dimension_type, sort_order
            FROM dimensions
            WHERE is_deleted = false
            ORDER BY sort_order
        """)).mappings().all()

        members = db.execute(text("""
            SELECT
                m.id,
                m.dimension_id,
                d.name AS dimension_name,
                m.code,
                m.name,
                m.display_name,
                m.sort_order
            FROM members m
            JOIN dimensions d ON d.id = m.dimension_id
            WHERE m.is_deleted = false
            ORDER BY d.sort_order, m.sort_order
        """)).mappings().all()

        measures = db.execute(text("""
            SELECT id, dataset_id, name, display_name, expression, aggregation, format_type, sort_order
            FROM measures
            WHERE is_deleted = false
            ORDER BY sort_order
        """)).mappings().all()

        fields = db.execute(text("""
            SELECT id, dataset_id, name, display_name, data_type, role, aggregation, format_type, sort_order
            FROM fields
            ORDER BY sort_order
        """)).mappings().all()

        return {
            "datasets": [dict(x) for x in datasets],
            "dimensions": [dict(x) for x in dimensions],
            "members": [dict(x) for x in members],
            "measures": [dict(x) for x in measures],
            "fields": [dict(x) for x in fields],
        }

    finally:
        db.close()