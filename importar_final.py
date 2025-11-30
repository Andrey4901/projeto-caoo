import json
import os
from pymongo import MongoClient

def importar_com_correcao():
    # 1. Conexão MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["sistema_atletas"]
    collection = db["jogadores"]

    arquivo = "jogadores.json"

    if not os.path.exists(arquivo):
        print("❌ Arquivo jogadores.json não encontrado.")
        return

    # 2. Carregar JSON
    with open(arquivo, "r", encoding="utf-8") as f:
        dados = json.load(f)

    print(f"📂 Processando {len(dados)} registros...")

    # Lista de nomes que JÁ existem no banco (para não duplicar os 4 que já funcionaram)
    nomes_no_banco = set(doc["Nome"] for doc in collection.find({}, {"Nome": 1}))
    
    novos_para_inserir = []

    # 3. Varredura e Limpeza
    for item in dados:
        atleta_limpo = {}
        
        # Corrige as chaves uma por uma
        for chave, valor in item.items():
            # Remove espaços em branco antes e depois da chave!
            # Ex: "Nome " vira "Nome"
            chave_limpa = chave.strip() 
            
            # Padronização extra de segurança
            if chave_limpa.lower() == "nome":
                chave_limpa = "Nome"
            elif chave_limpa.lower() in ["data nasc", "nascimento"]:
                chave_limpa = "Data nasc"
            elif chave_limpa.lower() == "peso":
                chave_limpa = "peso" # Força minúsculo conforme padrão do sistema
            
            # Tratamento de valores Nulos (null no JSON vira None no Python)
            # Para o gráfico não quebrar, vamos transformar None em 0.0 nos campos numéricos
            if valor is None and chave_limpa in ['peso', 'estatura', 'flexibilidade', 'abdominal', 'arremesso', 'Salto horizontal', 'Salto vertical']:
                valor = 0.0

            # Remove espaços extras nos valores de texto também (Ex: " Marcelo" -> "Marcelo")
            if isinstance(valor, str):
                valor = valor.strip()

            atleta_limpo[chave_limpa] = valor

        # Verifica se temos um Nome válido e se ele já não está no banco
        nome = atleta_limpo.get("Nome")
        if nome and nome not in nomes_no_banco:
            novos_para_inserir.append(atleta_limpo)
            nomes_no_banco.add(nome) # Adiciona ao set local para não duplicar no loop

    # 4. Inserção
    if novos_para_inserir:
        collection.insert_many(novos_para_inserir)
        print(f"✅ SUCESSO! {len(novos_para_inserir)} atletas recuperados e importados.")
    else:
        print("⚠️ Nenhum dado novo encontrado (todos já estavam no banco ou arquivo inválido).")

if __name__ == "__main__":
    importar_com_correcao()