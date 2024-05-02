from threading import Thread

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
	return {"message": "Server is Online."}

@app.head("/")
async def head_root():
	return {"message": "Server is Online. [HEAD Method]"}

def start():
	uvicorn.run(app, host="0.0.0.0", port=8080)
