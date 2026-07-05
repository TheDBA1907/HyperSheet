from fastapi import FastAPI

app = FastAPI(title="HyperSheet API")


@app.get("/")
def root():
    return {
        "application": "HyperSheet",
        "status": "running"
    }
