from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from database import get_database_connection
import bcrypt

app = FastAPI()

class User(BaseModel):
    phone: str
    apiKey: str
    cycle: int

class AuthUser(BaseModel):
    user: str
    passw: str

class Cycle(BaseModel):
    date: str
    cycle: int

class InsertCyclesRequest(BaseModel):
    authUser: AuthUser
    cycles: List[Cycle]

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

@app.post("/users")
async def read_users(authUser : AuthUser):
    if not verify_user(authUser):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    connection = get_database_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM whatsapp_users"
    cursor.execute(query)
    users = cursor.fetchall()
    connection.close()
    return users

@app.post("/cycles/max-date")
async def get_max_date(authUser: AuthUser):
    if not verify_user(authUser):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    connection = get_database_connection()
    cursor = connection.cursor()
    
    query = "SELECT date, cycle FROM cycles_calendar ORDER BY TO_DATE(date, 'DD/MM') DESC LIMIT 1"
    cursor.execute(query)
    result = cursor.fetchall()

    connection.close()
    return result

@app.post("/cycles/insert")
async def insert_cycles(request: InsertCyclesRequest):
    if not verify_user(request.authUser):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not request.cycles:
        raise HTTPException(status_code=400, detail="No se recibió información para insertar.")
    
    connection = get_database_connection()
    cursor = connection.cursor()
    
    delete_query = "DELETE FROM cycles_calendar"
    cursor.execute(delete_query)
    
    insert_query = "INSERT INTO cycles_calendar (date, cycle) VALUES (%s, %s)"
    data_to_insert = [(cycle.date, cycle.cycle) for cycle in request.cycles]
    
    cursor.executemany(insert_query, data_to_insert)
    
    connection.commit()
    connection.close()
    
    return {"message": "Datos insertados correctamente.", "filas_insertadas": len(request.cycles)}

def verify_user(authUser : AuthUser):
    connection = get_database_connection()
    cursor = connection.cursor()
    
    query = "SELECT password FROM authusers WHERE username = %s"
    cursor.execute(query, (authUser.user,))
    result = cursor.fetchone()
    
    connection.close()
    
    if result is None:
        return False
    
    hashed_password = result[0]
    return bcrypt.checkpw(authUser.passw.encode(), hashed_password.encode())
