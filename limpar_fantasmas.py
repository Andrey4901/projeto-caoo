from pymongo import MongoClient

def limpar_fantasmas():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["sistema_atletas"]
    collection = db["jogadores"]

    print("👻 Caçando registros fantasmas...")

    # 1. Padronizar: Se tiver 'nome' minúsculo, renomeia para 'Nome'
    # O MongoDB permite update com $rename
    collection.update_many({}, {"$rename": {"nome": "Nome"}})
    
    # 2. Apagar registros que NÃO têm 'Nome' ou NÃO têm 'peso'
    # Isso elimina logins antigos, usuários admin, e dados corrompidos
    resultado = collection.delete_many({
        "$or": [
            {"Nome": {"$exists": False}},
            {"peso": {"$exists": False}},
            {"Nome": "nan"}
        ]
    })

    print(f"✅ Limpeza concluída! {resultado.deleted_count} registros inválidos foram removidos.")

if __name__ == "__main__":
    limpar_fantasmas()