from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.config import settings
from api.service import routers

app = FastAPI(**settings.fastapi_settings)
app.include_router(routers)
app.add_middleware(CORSMiddleware, **settings.cors)
