from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.api.routes_health import router as health_router
from backend.app.api.routes_documents import router as documents_router
from backend.app.api.routes_matches import router as matches_router
from backend.app.api.routes_companies import router as companies_router
from backend.app.db.session import init_db


def create_app() -> FastAPI:
    # Initialize DB (creates tables)
    init_db()

    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0"
    )

    # CORS (allow frontend to access backend)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Routers
    app.include_router(health_router, prefix="/api", tags=["Health"])
    app.include_router(documents_router, prefix="/api", tags=["Documents"])
    app.include_router(matches_router, prefix="/api", tags=["Matching"])
    app.include_router(companies_router, prefix="/api", tags=["Companies"])

    return app


app = create_app()
