import logging
from argparse import ArgumentParser

import uvicorn
from demo_project.api.api_v1.api import api_router
from demo_project.api.dependencies import azure_scheme
from demo_project.core.config import settings
from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware

log = logging.getLogger(__name__)

app = FastAPI(
    openapi_url=f'{settings.API_V1_STR}/openapi.json',
    swagger_ui_oauth2_redirect_url='/oauth2-redirect',
    swagger_ui_init_oauth={
        'usePkceWithAuthorizationCodeGrant': True,
        'clientId': settings.OPENAPI_CLIENT_ID,
        # 'additionalQueryStringParams': {'prompt': 'consent'},
    },
    version='1.0.0',
    description='## Welcome to my API! \n This is my description, written in `markdown`',
    title=settings.PROJECT_NAME,
)


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:  # pragma: no cover
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


@app.on_event('startup')
async def load_config() -> None:
    """
    Load OpenID config on startup.
    """
    await azure_scheme.openid_config.load_config()


app.include_router(
    api_router,
    prefix=settings.API_V1_STR,
    dependencies=[Security(azure_scheme, scopes=['user_impersonation'])],
)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--api', action='store_true')
    parser.add_argument('--reload', action='store_true')
    args = parser.parse_args()
    if args.api:
        uvicorn.run('main:app', reload=args.reload)
    else:
        raise ValueError('No valid combination of arguments provided.')
