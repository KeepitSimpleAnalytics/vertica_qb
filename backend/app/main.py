from fastapi import FastAPI
from .routers import auth

app = FastAPI(title="Vertica Query Tool API")

# Include the authentication router
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"status": "API is running"}