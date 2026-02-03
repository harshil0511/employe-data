import time
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.api import employees, companies, company_dashboard, logs
from app.database import database
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.core.logger import mongo_logger

# Initialize FastAPI app
app = FastAPI(
    title="Employee & Company Core API",
    description="Separated CRUD with Connected Keys",
    version="1.0.0"
)

@app.middleware("http")
async def audit_log_middleware(request: Request, call_next):
    start_time = time.time()
    path = request.url.path
    method = request.method
    client_host = request.client.host if request.client else "unknown"
    
    try:
        response = await call_next(request)
        status_code = response.status_code
        exception_msg = None
    except Exception as e:
        status_code = 500
        exception_msg = str(e)
        # We don't re-raise here because FastAPI handles errors, 
        # but in a middleware we might need to if we want the default handler to take over.
        # Actually, call_next usually returns a response even for errors unless it's a catastrophic failure.
        raise e
    finally:
        process_time = time.time() - start_time
        
        # Log the API Audit event
        log_level = "INFO" if status_code < 400 else "ERROR"
        
        mongo_logger.log(
            level=log_level,
            message=f"API Audit: {method} {path} - {status_code}",
            details={
                "type": "audit_log",
                "method": method,
                "path": path,
                "status_code": status_code,
                "client_ip": client_host,
                "process_time_ms": round(process_time * 1000, 2),
                "query_params": str(request.query_params),
                "error": exception_msg
            }
        )
    
    return response

# Routes
app.include_router(company_dashboard.router, prefix="/api")
app.include_router(employees.router, prefix="/api")
app.include_router(companies.router, prefix="/api")
app.include_router(logs.router, prefix="/api")

# Static and Templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
def root():
    return {"message": "System is running"}

@app.get("/dashboard", response_class=HTMLResponse)
@app.get("/dashboard.html", response_class=HTMLResponse)
@app.get("/html-dashboard", response_class=HTMLResponse)
@app.get("/html.dashboard", response_class=HTMLResponse)
def dashboard_view(request: Request, db: Session = Depends(database.get_db)):
    try:
        data = company_dashboard.top_five_companies_with_top_employee(db)
    except Exception:
        data = []
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "data": data}
    )
