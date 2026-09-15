from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Mathdyl Academy API",
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy"
    }