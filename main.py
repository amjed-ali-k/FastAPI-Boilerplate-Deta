import fastapi
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from api import auth
import uvicorn
from views import home
from config import settings

app = fastapi.FastAPI(title="BoilerPlate - Amjed Ali",
                      description="This is a very fancy project, with auto docs for the API and everything",
                      version="2.5.0", )


def configure():
    configure_middlewares()
    configure_routing()


def configure_middlewares():
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin)
                       for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def configure_routing():
    app.mount('/static', StaticFiles(directory='static'), name='static')
    app.include_router(home.router)
    app.include_router(auth.router)


if __name__ == '__main__':
    configure()
    uvicorn.run("main:app", port=8000, host="127.0.0.1", reload=True)
else:
    configure()
