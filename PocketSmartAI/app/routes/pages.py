from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.dependencies import get_current_user
from app.models.db import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def page(template: str, request: Request, user: User | None = None):
    return templates.TemplateResponse(template, {"request": request, "user": user})

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return page("index.html", request)

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return page("login.html", request)

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return page("register.html", request)

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user: User = Depends(get_current_user)):
    return page("dashboard.html", request, user)

@router.get("/home-planner", response_class=HTMLResponse)
def home_planner(request: Request, user: User = Depends(get_current_user)):
    return page("home_planner.html", request, user)

@router.get("/party-planner", response_class=HTMLResponse)
def party_planner(request: Request, user: User = Depends(get_current_user)):
    return page("party_planner.html", request, user)

@router.get("/jewelry-planner", response_class=HTMLResponse)
def jewelry_planner(request: Request, user: User = Depends(get_current_user)):
    return page("jewelry_planner.html", request, user)

@router.get("/history", response_class=HTMLResponse)
def history(request: Request, user: User = Depends(get_current_user)):
    return page("history.html", request, user)
