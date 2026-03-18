from fastapi import FastAPI

from app.routes.billing import router

app = FastAPI(
    title="Orbital Witness Usage API",
    description="Calculates credit usage for the current billing period",
)

app.include_router(router)
