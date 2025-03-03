from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from database import get_database_connection

app = FastAPI()

class User(BaseModel):
    phone: str
    apiKey: str
    cycle: int

@app.post("/register-user")
async def create_user(user : User):
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "INSERT INTO whatsapp_users (phone, api_key, cycle) VALUES (%s, %s, %s)"
    values = (user.phone, user.apiKey, user.cycle)
    cursor.execute(query, values)
    connection.commit()
    connection.close()
    return {"message": "User created!"}

@app.get("/users")
async def read_users():
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM whatsapp_users"
    cursor.execute(query)
    users = cursor.fetchall()
    connection.close()
    return users