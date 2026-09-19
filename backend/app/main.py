from fastapi import FastAPI

from app.routes import router


app = FastAPI(title="Academic Damage Control API")
app.include_router(router)
