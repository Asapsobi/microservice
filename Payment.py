from fastapi import FastAPI
import asyncio
from redis_om import get_redis_connection , HashModel
from fastapi.background import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
import requests ,time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000/"],
    allow_methods=["*"],
    allow_headers=["*"]
)



redis = get_redis_connection(
    host="localhost",
    port=6379,
    # password="kNgEQkIVzIoQ33edbXFZQPuvlzX1abOr",
    # decode_responses=True,
)


class Order (HashModel) :
    product_id:str
    price: float 
    fee : float
    total : float
    quantity : int
    status : str #pending , completed , refunded

    class Meta :
        database = redis


@app.get ("/orders/{pk}")
def get(pk : str) :
    order= Order.get (pk)
    redis.xadd("refund_order",order.dict , "*")
    return order

@app.post("/orders")
async def create(request : Request , background_tasks : BackgroundTasks) :
    body = await request.json()

    req = requests.get ("http://localhost:8000/products/%s" %body["id"])
    product=req.json()

    order =Order(
        product_id=body["id"],
        price=product["price"],
        fee=0.2*product["price"],
        total=1.2 * product["price"],
        quantity=body["quantity"],
        status="pending"
    )
    order.save()
    background_tasks.add_task(order_completed,order)

    return order

def order_completed(order:Order) :
    time.sleep (1)
    order.status="completed"
    order.save()
    redis.xadd("order_completed",order.dict(),"*")