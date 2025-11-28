import json
from pymongo import MongoClient

# 1. Conexão com o Banco Local
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["sistema_atletas"]
    collection = db["jogadores"]
    print("Conectado ao MongoDB!")
except Exception as e:
    print(f"Erro ao conectar: {e}")
    exit()

# 2. Ler o JSON antigo
nome_arquivo = "jogadores.json" # Ou o nome que você usava antes, ex: jogadores.json
try:
    with open(nome_arquivo, "r", encoding="utf-8") as f:
        dados_antigos = json.load(f)
        print(f"Lidos {len(dados_antigos)} jogadores do arquivo JSON.")
except FileNotFoundError:
    print("Arquivo JSON não encontrado. Começando banco vazio.")
    dados_antigos = []

# 3. Salvar no MongoDB
if dados_antigos:
    # Limpa a coleção antes para não duplicar (opcional)
    # collection.delete_many({}) 
    
    # Insere os dados
    collection.insert_many(dados_antigos)
    print("Sucesso! Dados transferidos para o MongoDB.")
else:
    print("Nenhum dado para migrar.")