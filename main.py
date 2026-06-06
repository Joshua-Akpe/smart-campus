from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from database import engine, Base
import models
from routers import users
from routers import complaints
from routers import admin

#create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Campus Feedback System")

#mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")


# Register routers
app.include_router(users.router)
app.include_router(complaints.router)
app.include_router(admin.router)

#root
@app.get("/")
def root():
    return RedirectResponse(url="/login")

#error handlers
@app.exception_handler(401)
async def unauthorized_handler(request: Request, exc: HTTPException):
    return RedirectResponse(url="/login")