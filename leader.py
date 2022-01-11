#!/usr/bin/env python
#
# Description: This is a simple leaderboard display application, for presenting a 
# user leaderboard of data. The application provides a simple way of capturing and
# displaying of 'at event' challenge data. Data are persistent and stored in a DB.
# 
from fastapi import FastAPI, Query
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.validators import RegexValidator

import pandas as pd
import re

app = FastAPI()

# Added to create path to static files for linking CSS file
app.mount("/static", StaticFiles(directory="templates"),name="static")

class Users(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=50, unique=True, validators=[RegexValidator(
        '^[a-z0-9]+[\._]?[ a-z0-9]+[@]\w+[. ]\w{2,3}$',re.IGNORECASE)])
    first = fields.CharField(max_length=25)
    last  = fields.CharField(max_length=25)
    time_taken  = fields.SmallIntField(default=0, pk=False)

    
Users_Pydantic = pydantic_model_creator(Users, name='Users')
UsersIn_Pydantic = pydantic_model_creator(Users, name='UsersIn', exclude_readonly=True)


@app.get('/')
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

templates = Jinja2Templates(directory="templates")

@app.get('/leaders')
async def get_users(request: Request):
    users = await UsersIn_Pydantic.from_queryset(Users.all())
    # Sort users by the fastest time taken to complete the challenge
    users.sort(key=lambda x: x.time_taken)
    users_dict = []
    for x in users: users_dict.append(x.__dict__)
    df = pd.DataFrame(users_dict)
    return templates.TemplateResponse('index.html', context={'request': request, 'data': df.to_html()})

@app.get('/getuser/{id}')
async def get_user(user_id: int):
    return await Users_Pydantic.from_queryset_single(Users.get(id=user_id))

@app.get('/getuser')
async def get_user_by_email(email_addr: str = Query(default=None,description="Please enter user email addr")):
    users = await Users_Pydantic.from_queryset(Users.filter(email=email_addr))
    if len(users) > 0:
        return {f"Found user with email {email_addr}" : f"id = {users[0].id}"  }
    else:
        return {'Error' : f'User {email_addr} not found'}

@app.post('/createuser')
async def create_user(user: UsersIn_Pydantic):
    user_obj = await Users.create(**user.dict(exclude_unset=True))
    return await Users_Pydantic.from_tortoise_orm(user_obj)

@app.delete('/leaders/{user_id}')
async def delete_user(user_id: int):
    await Users.filter(id=user_id).delete()
    return {"Success": "User deleted"}

register_tortoise(
    app,
    db_url='sqlite://db.sqlite3',
    modules={'models': ['leader']},
    generate_schemas=True,
    add_exception_handlers=True
)
