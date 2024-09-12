import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.database import Database
from modules.bangumidata.bangumidata import *


@asynccontextmanager
async def lifespan(App: FastAPI):
    initRouter()
    if not os.path.exists("data"):
        os.makedirs("data")
        Database.init(BangumiData.getFromSource())
    else:
        pass
    yield
    
App = FastAPI(lifespan=lifespan)

App.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Config = uvicorn.Config(App, host="0.0.0.0", port=8964, log_level="info", reload=False,)

Server = uvicorn.Server(Config)


def initRouter():
    from api.api import api_router
    App.include_router(api_router, prefix="/api/v1")
    
        
if __name__ == '__main__':
    Server.run()