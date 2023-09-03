from fastapi import FastAPI
import asyncio
from redis_om import get_redis_connection , HashModel
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
redis = get_redis_connection(
    host="localhost",
    port=6379,
    # password="kNgEQkIVzIoQ33edbXFZQPuvlzX1abOr",
    # decode_responses=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000/"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class Product (HashModel) :
    name : str 
    price : float 
    quantity : int

    class Meta:
        database = redis


@app.get("/products")
def all () :
    return [format(pk) for pk in Product.all_pks()]

def format(pk:str) :
    product = Product.get (pk) 

    return {
        "id" : product.pk , 
        "name" :product.name ,
        "price" : product.price , 
        "quantity" : product.quantity
    }


@app.post("/products")
def create(product: Product) :
    return product.save()
    

@app.get("/products/{pk}")
def get (pk:str):
    return Product.get(pk)

@app.delete("/products/{pk}")
def delete(pk:str):
    return Product.delete(pk)