from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

app = FastAPI(title="Python Togo")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# Simple in-memory sample data
SAMPLE_EVENTS = [
    {"id": 1, "date": "2025-12-05", "location": "Lomé", "title": "Atelier Python débutant", "description": "Introduction à Python pour les nouveaux développeurs."},
    {"id": 2, "date": "2026-01-20", "location": "Lomé", "title": "Data Science avec Python", "description": "Atelier sur les bases de la data science."}
]

SAMPLE_NEWS = [
    {"id": 1, "date": "2025-11-01", "title": "Lancement d'un nouvel atelier Python", "excerpt": "Nous organisons un atelier sur les bases de Python."},
    {"id": 2, "date": "2025-09-15", "title": "Rencontre communautaire à Lomé", "excerpt": "Retour sur la rencontre mensuelle."}
]

SAMPLE_COMMUNITIES = [
    {"id": 1, "name": "Python Lomé", "description": "Groupe local basé à Lomé.", "city": "Lomé"}
]

TRANSLATIONS = {
    "fr": {
        "site-title": "Python Togo",
        "nav-home": "Accueil",
    },
    "en": {
        "site-title": "Python Togo",
        "nav-home": "Home",
    }
}

current_year = date.today().strftime("%Y")

class JoinRequest(BaseModel):
    name: str
    email: str
    phone: str | None = None
    city: str | None = None
    level: str | None = None
    interests: str | None = None


class ContactRequest(BaseModel):
    name: str
    email: str
    subject: str
    message: str


class PartnershipRequest(BaseModel):
    organization: str
    contact_name: str
    email: str
    website: Optional[str] = None
    message: Optional[str] = None


# In-memory holders for partnership requests and partners
PARTNERS = [
    {"name": "Python Software Foundation", "website": "https://www.python.org/", "logo_url": "https://res.cloudinary.com/dvg7vky5o/image/upload/b_rgb:457FAB/c_crop,w_1000,h_563,ar_16:9,g_auto/v1750463364/psf-logo_gqppfi.png"},
    {"name": "Association Francophone de Python", "website": "https://www.afpy.org/", "logo_url": "https://res.cloudinary.com/dvg7vky5o/image/upload/v1757104352/afpy_mizqfd.png"},
    {"name": "Django Software Foundation", "website": "https://www.djangoproject.com/", "logo_url": "https://res.cloudinary.com/dvg7vky5o/image/upload/v1757104362/django-logo-positive_ziry9u.png"},
    {"name": "Black Python Devs", "website": "https://blackpythondevs.com/index.html", "logo_url": "https://res.cloudinary.com/dvg7vky5o/image/upload/v1751558100/bpd_stacked_us5ika.png"},
    {"name": "O'REILLY", "website": "https://www.oreilly.com/", "logo_url": "https://res.cloudinary.com/dvg7vky5o/image/upload/v1763335940/oreilly_logo_mark_red_efvlhr.svg"},
    {"name": "GitBook", "website": "https://www.gitbook.com/", "logo_url": "https://res.cloudinary.com/dvg7vky5o/image/upload/v1763336328/GitBook_-_Dark_igckn1.png"},
    {"name": "Tahaga", "website": "https://tahaga.com/", "logo_url": "https://res.cloudinary.com/dvg7vky5o/image/upload/v1753966042/Logo_TAHAGA_02_Plan_de_travail_1_5_rh5s9g.jpg"},
    {"name": "DijiJob", "website": "https://wearedigijob.com", "logo_url": "https://res.cloudinary.com/dvg7vky5o/image/upload/v1755176153/digijoblogo_tkbhns.png"},
    {"name": "Microsoft Student Ambassadors Togo", "website": "https://www.youtube.com/@mlsatogo", "logo_url": "https://res.cloudinary.com/dvg7vky5o/image/upload/v1754294585/msftatogo_qrtxl9.png"},
    {"name": "GitHub", "website": "https://github.com/", "logo_url": "https://res.cloudinary.com/dvg7vky5o/image/upload/v1752712570/GitHub_Logo_pn7gcn.png"},
    {"name": "Kweku Tech", "website": "https://www.youtube.com/@KwekuTech", "logo_url": "https://res.cloudinary.com/dvg7vky5o/image/upload/v1754092403/kwekutech_v4l7qn.png"},
]
GALLERIES = [
    {"date": "2025-08-23", "title": "PyCon Togo 2025", "image": "https://res.cloudinary.com/dvg7vky5o/image/upload/v1747588996/Group_6_r7n6id.png", "link": "https://drive.google.com/drive/folders/1Xk8lejAQXBIPjPf1UHnuUmZJ5sEYNPM1?usp=sharing"},
    {"date": "2024-11-30", "title": "PyDay Togo 2024", "image": "https://res.cloudinary.com/dvg7vky5o/image/upload/v1763346354/WUL_0330_rnemnd.jpg", "link": "https://drive.google.com/drive/folders/1UCZgBjcAaztwCi5R74WRqI8oxbCe1DNC?usp=sharing"},
]
PARTNERSHIP_REQUESTS: List[dict] = []


# Template routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(name="home.html", request=request, context={"current_year": current_year, "partners": PARTNERS})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(name="about.html", request=request, context={"current_year": current_year})

@app.get("/events")
async def events(request: Request):
    return templates.TemplateResponse(request=request, name="events.html", context={"current_year": current_year})

@app.get("/actualities")
async def actualities(request: Request):
    return templates.TemplateResponse(request=request, name="actualites.html", context={"current_year": current_year})

@app.get("/communities")
async def communities(request: Request):
    return templates.TemplateResponse(request=request, name="communities.html", context={"current_year": current_year})

@app.get("/join")
async def join(request: Request):
    return templates.TemplateResponse(request=request, name="join.html", context={"current_year": current_year})

@app.get("/contact")
async def contact(request: Request):
    return templates.TemplateResponse(request=request, name="contact.html", context={"current_year": current_year})


@app.get("/code-of-conduct")
async def code_of_conduct(request: Request):
    return templates.TemplateResponse(request=request, name="code_of_conduct.html", context={"current_year": current_year})


@app.get("/partners")
async def partners(request: Request):
    return templates.TemplateResponse(request=request, name="partners.html", context={"current_year": current_year, "partners": PARTNERS})


@app.post('/api/v1/partnership')
async def partnership_submit(request: PartnershipRequest):
    PARTNERSHIP_REQUESTS.append(request.dict())
    # Here you would normally send an email or store the request in a DB
    return JSONResponse(content={"status": "received"})


@app.get('/gallery')
async def gallery(request: Request):
    # Placeholder gallery page — user can set external link via localStorage or update template
    return templates.TemplateResponse(request=request, name='gallery.html', context={"current_year": current_year, "galleries": GALLERIES})






if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=8080)
