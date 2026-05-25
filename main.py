from fastapi import *
from fastapi.responses import FileResponse

app = FastAPI()

import backend.endpoints.restaurants
import backend.endpoints.cart
import backend.endpoints.order
import backend.endpoints.users
import backend.endpoints.root

@app.get("/")
async def home():
    return FileResponse("frontend/home.html")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="localhost",
        port=9000,
        reload=True
    )
