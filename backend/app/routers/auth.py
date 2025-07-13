from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .. import security, models
import vertica_python
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

router = APIRouter(
    tags=["Authentication"]
)

@router.post("/token", response_model=models.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    # Get environment variables
    host = os.getenv("VERTICA_HOST")
    port = os.getenv("VERTICA_PORT")
    db = os.getenv("VERTICA_DB")

    logger.info(f"Attempting connection to Vertica:")
    logger.info(f"Host: {host}, Port: {port}, Database: {db}, User: {username}")

    # Validate environment variables
    if not all([host, port, db]):
        logger.error("Missing environment variables")
        missing = []
        if not host: missing.append("VERTICA_HOST")
        if not port: missing.append("VERTICA_PORT") 
        if not db: missing.append("VERTICA_DB")
        raise HTTPException(
            status_code=500, 
            detail=f"Server configuration error. Missing: {', '.join(missing)}"
        )

    conn_info = {
        'host': host,
        'port': int(port),
        'user': username,
        'password': password,
        'database': db,
        'connection_timeout': 30,  # Increased timeout
        'unicode_error': 'strict',
        'ssl': False,  # Explicitly disable SSL if not needed
    }

    try:
        logger.info("Attempting Vertica connection...")
        with vertica_python.connect(**conn_info) as connection:
            # Test the connection with a simple query instead of is_open()
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if not result:
                raise ConnectionError("Connection test query failed.")
            logger.info("Vertica connection successful!")
            
    except vertica_python.errors.ConnectionError as e:
        logger.error(f"Vertica connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to connect to database server. Please check network connectivity.",
        )
    except vertica_python.errors.DatabaseError as e:
        logger.error(f"Vertica database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {e}")
        # Check for specific error patterns
        error_str = str(e).lower()
        if "authentication" in error_str or "password" in error_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
        elif "timeout" in error_str or "network" in error_str:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection timeout. Please try again.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error. Please contact administrator.",
            )

    # Create and return access token
    access_token = security.create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}

# Add a health check endpoint
@router.get("/health")
async def health_check():
    """Check if the service can connect to Vertica"""
    host = os.getenv("VERTICA_HOST")
    port = os.getenv("VERTICA_PORT")
    db = os.getenv("VERTICA_DB")
    
    return {
        "status": "ok",
        "vertica_config": {
            "host": host,
            "port": port,
            "database": db,
            "host_reachable": bool(host),
            "port_valid": port and port.isdigit(),
            "database_set": bool(db)
        }
    }