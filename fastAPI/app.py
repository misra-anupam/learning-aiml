from pydantic import BaseModel, Annotated
from fastAPI import FastAPI, Query

app = FastAPI()

class APIInput(BaseModel):
    model_config = {"extra": "forbid"}
    message: str

class APIOutput(BaseModel):
    message: str


@app.get("/")
async def root(input_message:APIInput):
    return APIOutput({"message":input_message})

@app.get("/joke")
async def tell_joke(input_message: Annotated[str|None, Query(max_length=50)])