"""Run the demo app: python -m demo.app"""
import os

import uvicorn

if __name__ == "__main__":
    uvicorn.run("demo.app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
