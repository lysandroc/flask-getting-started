from itertools import count
from typing import Optional
from flask import Flask, request, jsonify
from flask_pydantic_spec import FlaskPydanticSpec, Response, Request
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query

server = Flask(__name__)
spec = FlaskPydanticSpec('flask', title='Python RestAPI')
spec.register(server)

database = TinyDB('database.json')
c = count()

class Pessoa(BaseModel):
    id: Optional[int] = Field(default_factory=lambda: next(c))
    nome: str
    idade: int

class Pessoas(BaseModel):
    pessoas: list[Pessoa]
    count: int

@server.get('/pessoas')
@spec.validate(resp=Response(HTTP_200=Pessoas))
def busca_pessoas():
    """ retorna todas as pessoas do banco de dados """
    pessoas = database.all()
    todas_pessoas = Pessoas(pessoas=pessoas, count=len(pessoas))
    return jsonify(todas_pessoas.dict())

@server.post('/pessoas')
@spec.validate(body=Request(Pessoa), resp=Response(HTTP_200=Pessoa))
def inseri_pessoa():
    """Insere uma Pessoa no banco de dados """
    body = request.context.body.dict()
    database.insert(body)
    return body

@server.put('/pessoas/<int:id>')
@spec.validate(body=Request(Pessoa), resp=Response(HTTP_200=Pessoa))
def altera_pessoa(id):
    Pessoa = Query()
    body = request.context.body.dict()
    database.update(body, Pessoa.id == id)
    return jsonify(body)

@server.delete('/pessoas/<int:id>')
@spec.validate(resp=Response(HTTP_204=Pessoa))
def deleta_pessoa(id):
    database.remove(Query().id == id)
    return jsonify({})

server.run()
