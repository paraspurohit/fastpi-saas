# start time :- 11:18
# finish by :- 2:30
# actual finished:- 4:38
# testing started: - 4:55
# pushed on : 8:30
import uvicorn
from fastapi import FastAPI
from app.middleware.middleware import middleware_handler
from app.routes import users, login
from prometheus_fastapi_instrumentator import Instrumentator

# from app.middleware.rate_limit import RateLimitMiddleware


app = FastAPI()

Instrumentator().instrument(app).expose(app)

# Base.metadata.create_all(bind=engine)
app.include_router(login.router)
app.include_router(users.router)
app.middleware("http")(middleware_handler)

# app.add_middleware(RateLimitMiddleware)


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run(app)
# alembic revision --autogenerate -m "baseline"
# alembic upgrade head
