from fastapi import APIRouter

router = APIRouter()


@router.get("/system/info")
def get_system_info():
    return {
        "application": "HyperSheet",
        "version": "0.0.1",
        "environment": "development",
        "database": "disconnected",
        "ai": "disabled"
    }
