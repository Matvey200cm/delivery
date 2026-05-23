from fastapi import FastAPI

app = FastAPI()

import backend.endpoints.restaurants
import backend.endpoints.cart
import backend.endpoints.order
import backend.endpoints.users
import backend.endpoints.root

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True
    )