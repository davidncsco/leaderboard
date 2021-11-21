#!/usr/bin/env python
#
# Copyright (c) 2021  David Nguyen <davidn@cisco.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
# Description: This is a simple leaderboard display application, for presenting a 
# user leaderboard of data. The python app provides a simple way of capturing and
# displaying of 'at event' challenge data.
# 
from fastapi import FastAPI
from fastapi import Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

import pandas as pd

app = FastAPI()

class Users(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=50, unique=True)
    first = fields.CharField(max_length=25)
    last  = fields.CharField(max_length=25)
    time_taken  = fields.IntField(pk=False)

Users_Pydantic = pydantic_model_creator(Users, name='Users')
UsersIn_Pydantic = pydantic_model_creator(Users, name='UsersIn', exclude_readonly=True)

@app.get('/')
def index():
    return ["DevNet Custome Success Leaderboard Display"]

templates = Jinja2Templates(directory="templates")

@app.get('/leaders')
async def get_users(request: Request):
    users = await Users_Pydantic.from_queryset(Users.all())
    # Sort users by the fastest time taken to complete the challenge
    users.sort(key=lambda x: x.time_taken)
    users_dict = []
    for x in users: users_dict.append(x.__dict__)
    df = pd.DataFrame(users_dict)
    return templates.TemplateResponse('form.html', context={'request': request, 'data': df.to_html()})

@app.get('/leaders/{id}')
async def get_user(user_id: int):
    return await Users_Pydantic.from_queryset_single(Users.get(id=user_id))

@app.post('/leaders')
async def create_user(user: UsersIn_Pydantic):
    user_obj = await Users.create(**user.dict(exclude_unset=True))
    return await Users_Pydantic.from_tortoise_orm(user_obj)

@app.delete('/leaders/{user_id}')
async def delete_user(user_id: int):
    await Users.filter(id=user_id).delete()
    return {}

register_tortoise(
    app,
    db_url='sqlite://db.sqlite3',
    modules={'models': ['leader']},
    generate_schemas=True,
    add_exception_handlers=True
)
