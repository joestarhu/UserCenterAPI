from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from api.config import settings
from api.service import routers

app = FastAPI(**settings.fastapi_settings)
app.add_middleware(CORSMiddleware, **settings.cors)
app.include_router(routers)
