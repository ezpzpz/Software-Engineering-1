from fastapi import FastAPI
from pydantic import BaseModel
import subprocess


app = FastAPI()


class Item(BaseModel):
    text: str


class Timer(BaseModel):
    h: int
    m: int
    s: int


# list_of_names = []
dict_of_names = {

}

current_timers = []


@app.get("/")
async def root():
    return dict_of_names


@app.post("/")
async def create_item(item: Item):
    # list_of_names.append(item)
    dict2 = item.dict()

    dict_of_names["text"] = dict2["text"]
    # print(list_of_names)
    return dict_of_names


@app.post("/timer")
async def create_timer(timer: Timer):

    # subprocess.run(["python", "timer.py"])

    current_timers.append(timer)
    return current_timers


@app.get("/timer")
async def timer():
    return current_timers


@app.put("/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}
