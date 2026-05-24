from main import app

@app.get("/")
async def root():
    return {
        "message": "Доставка еды API",
        "version": "4.0",
        "endpoints": {
            "restaurants": "/api/restaurants",
            "search": "/api/search?query=пицца",
            "menu": "/api/restaurants/2/menu",
            "cart": "/api/cart/{session_id}"
        }
    }