

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pymongo import MongoClient
from pydantic import BaseModel, Field
from bson import ObjectId
import os


load_dotenv()

app = FastAPI()

class Produto(BaseModel):
    nome: str
    preco: float = Field(gt=0)
    categoria: str
    estoque: int = Field(ge=0)

class AtualizacaoProduto(BaseModel):
    nome: str | None = None
    preco: float | None = Field(default=None, gt=0)
    categoria: str | None = None
    estoque: int | None = Field(default=None, ge=0)


MONGO_URI = os.getenv("MONGO_URI")

cliente = MongoClient(MONGO_URI)
banco = cliente["loja"]
produtos = banco["produtos"]


@app.get("/")
def inicio():
    return {"mensagem": "Minha API está funcionando!"}


@app.get("/testar-banco")
def testar_banco():
    cliente.admin.command("ping")
    return {"mensagem": "Conexão com MongoDB funcionando!"}


@app.post("/produtos")
def cadastrar_produto(produto: Produto):
    dados = produto.model_dump()
    resultado = produtos.insert_one(dados)

    return {
        "mensagem": "Produto cadastrado com sucesso!",
        "id": str(resultado.inserted_id)
    }


@app.get("/produtos/{produto_id}")
def buscar_produto(produto_id: str):
    if not ObjectId.is_valid(produto_id):
        raise HTTPException(
            status_code=400,
            detail="ID do produto inválido"
        )

    produto = produtos.find_one(
        {"_id": ObjectId(produto_id)}
    )

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    produto["_id"] = str(produto["_id"])
    return produto


@app.get("/produtos")
def listar_produtos():
    lista = []

    for produto in produtos.find():
        produto["_id"] = str(produto["_id"])
        lista.append(produto)

    return lista


@app.delete("/produtos/{produto_id}")
def excluir_produto(produto_id: str):
    if not ObjectId.is_valid(produto_id):
        raise HTTPException(
            status_code=400,
            detail="ID do produto inválido"
        )

    resultado = produtos.delete_one({"_id": ObjectId(produto_id)})

    if resultado.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    return {"mensagem": "Produto excluído com sucesso!"}


@app.put("/produtos/{produto_id}")
def atualizar_produto(produto_id: str, produto: Produto):
    if not ObjectId.is_valid(produto_id):
        raise HTTPException(
            status_code=400,
            detail="ID do produto inválido"
        )

    resultado = produtos.update_one(
        {"_id": ObjectId(produto_id)},
        {"$set": produto.model_dump()}
    )

    if resultado.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    return {"mensagem": "Produto atualizado com sucesso!"}


@app.patch("/produtos/{produto_id}")
def atualizar_parcialmente(
    produto_id: str,
    dados: AtualizacaoProduto
):
    if not ObjectId.is_valid(produto_id):
        raise HTTPException(
            status_code=400,
            detail="ID do produto inválido"
        )
    atualizacoes = dados.model_dump(exclude_unset=True)

    if not atualizacoes:
        raise HTTPException(
            status_code=400,
            detail="Envie pelo menos um campo para atualizar"
        )

    resultado = produtos.update_one(
        {"_id": ObjectId(produto_id)},
        {"$set": atualizacoes}
    )

    if resultado.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    return {"mensagem": "Produto atualizado parcialmente!"}




    


