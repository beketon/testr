import logging
import sys

import sentry_sdk
from fastapi import FastAPI, Request, Response
from starlette.middleware.cors import CORSMiddleware

from src.action_history.router import router as action_history_router
from src.clients.sendgrid import mail_client
from src.common.models import SendEmail
from src.common.router import router as common_router
from src.config import app_configs, settings
from src.constants import Environment
from src.directions.router import router as directions_router
from src.expenses.router import router as expense_router
from src.geography.router import router as router_geography
from src.geography.utils import init_data
from src.orders.router import router as router_orders
from src.shipping.router import router as shipping_router
from src.statistics.router import router as router_statistics
from src.tarifs.router import router as router_tarifs
from src.transportation_types.router import \
    router as transportation_types_router
from src.users.router import router as router_users
from src.warehouse.router import router as router_warehouse

if settings.ENVIRONMENT != Environment.LOCAL:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
        environment=settings.ENVIRONMENT.value
    )

if settings.ENVIRONMENT != Environment.LOCAL:
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG
    )

logger = logging.getLogger(__name__)

app = FastAPI(debug=settings.ENVIRONMENT.is_debug, **app_configs)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_users)
app.include_router(router_orders)
app.include_router(router_geography)
app.include_router(router_warehouse)
app.include_router(directions_router)
app.include_router(common_router)
app.include_router(expense_router)
app.include_router(shipping_router)
app.include_router(action_history_router)
app.include_router(router_statistics)
app.include_router(transportation_types_router)
app.include_router(router_tarifs)


@app.on_event('startup')
async def startup_event_setup():
    await init_data()


@app.post("/api/v1/send-email", tags=["email"])
async def send_email(send_email: SendEmail):
    return mail_client.send(send_email)


@app.middleware("http")
async def api_logging(request: Request, call_next):
    response = await call_next(request)

    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk
    log_message = {
        "host": request.url.hostname,
        "endpoint": request.url.path,
        "response": response_body.decode("utf-8", "ignore"),
        "status_code": response.status_code,
        "method": request.method,
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "user_agent": request.headers.get("user-agent")
    }
    logger.debug(log_message)
    return Response(content=response_body, status_code=response.status_code,
                    headers=dict(response.headers), media_type=response.media_type)
