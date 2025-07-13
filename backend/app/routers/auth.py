from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .. import security, models
import vertica_python
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    tags=["Authentication"]
)

@router.post("/token", response_model=models.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    # --- PRE-CONNECTION DEBUGGING ---
    host = os.getenv("VERTICA_HOST")
    port = os.getenv("VERTICA_PORT")
    db = os.getenv("VERTICA_DB")

    print("--- ATTEMPTING CONNECTION WITH: ---")
    print(f"Host: {host} (Type: {type(host)})")
    print(f"Port: {port} (Type: {type(port)})")
    print(f"Database: {db} (Type: {type(db)})")
    print("---------------------------------")

    if not all([host, port, db]):
        print("ERROR: One or more environment variables are missing.")
        raise HTTPException(status_code=500, detail="Server configuration error.")

    conn_info = {
        'host': host,
        'port': int(port),
        'user': username,
        'password': password,
        'database': db,
        'connection_timeout': 10
    }

    try:
        with vertica_python.connect(**conn_info) as connection:
            if not connection.is_open():
                 raise ConnectionError("Connection was not opened.")
    except Exception as e:
        print(f"!!! DETAILED VERTICA ERROR: {e} !!!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = security.create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}
