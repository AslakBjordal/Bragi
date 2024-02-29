from fastapi import FastAPI
from fastapi import FastAPI, Response

app = FastAPI()


@app.get("/")
async def read_root():
    text = "I like red bull"
    return Response(status_code=200, content=text)



# app.include_router()
