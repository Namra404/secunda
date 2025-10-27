import asyncio

import uvicorn
from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware

from configuration.security import require_api_key
from presentation.api.routes import building_router, activity_router, organization_router

app = FastAPI(
    title='Secunda test API',
    description='API для тестового задания secunda',
    version='0.1.0',
    dependencies=[Depends(require_api_key)],
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


app.include_router(building_router.router)
app.include_router(activity_router.router)
app.include_router(organization_router.router)


async def start_app():
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        log_level='info',
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == '__main__':
    asyncio.run(start_app())