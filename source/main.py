import uvicorn
from fastapi import FastAPI
from sqlmodel import SQLModel
from fastapi.middleware.cors import CORSMiddleware
from router import bot_router
from Database.sqlDB import engine


from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield  # Application startup

#app = FastAPI(lifespan=lifespan)
app = FastAPI()

origins = [
  "http://97.74.92.197:3002/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(bot_router.router,prefix="/api")



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)


#http://127.0.0.1:8000/docs