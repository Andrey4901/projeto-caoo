import json
import os
from pymongo import MongoClient

def restaurar_inteligente():
    # 1. Conexão
    client = MongoClient("mongodb://localhost:27017/")
    db = client["sistema_atletas"]
    collection = db["jogadores"]

    arquivo_backup = "jogadores.json" # Certifique-se que o nome está correto

    if not os.path.exists(arquivo_backup):
        print(f"❌ Erro: Arquivo '{arquivo_backup}' não encontrado.")
        return

    # 2. Carrega os dados do arquivo
    try:
        with open(arquivo_backup, "r", encoding="utf-8") as f:
            dados_antigos = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao ler JSON: {e}")
        return

    print(f"📂 Arquivo carregado. Analisando {len(dados_antigos)} registros...")

    # 3. Mapeamento de Correção (De -> Para)
    # Isso resolve o problema de letras minúsculas ou nomes diferentes
    mapa_chaves = {
        "nome": "Nome",
        "usuario": "Nome", # Caso venha do arquivo de login
        "nascimento": "Data nasc",
        "data_nascimento": "Data nasc",
        "dt_nasc": "Data nasc",
        "Peso": "peso", # O sistema usa minúsculo para medidas
        "Estatura": "estatura",
        "Altura": "estatura"
    }

    # Lista dos nomes que JÁ estão no banco (para não duplicar)
    nomes_existentes = set(doc["Nome"] for doc in collection.find({}, {"Nome": 1}))
    
    novos_registros = []
    recuperados = 0

    for item in dados_antigos:
        novo_atleta = {}
        
        # Copia e renomeia as chaves
        for chave, valor in item.items():
            chave_corrigida = mapa_chaves.get(chave, chave) # Se não tiver no mapa, usa a original
            # Se a chave corrigida for 'Nome' ou 'Data nasc', forçamos a primeira letra maiúscula se for string
            novo_atleta[chave_corrigida] = valor

        # Validação Básica: Precisa ter Nome
        nome_atleta = novo_atleta.get("Nome")
        
        if nome_atleta:
            # Se NÃO existe no banco, adicionamos à lista de restauração
            if nome_atleta not in nomes_existentes:
                
                # Garante que campos numéricos existam (mesmo que 0) para o gráfico não quebrar
                campos_fisicos = ['peso', 'estatura', 'flexibilidade', 'abdominal', 'arremesso', 'Salto horizontal', 'Salto vertical']
                for campo in campos_fisicos:
                    if campo not in novo_atleta:
                        novo_atleta[campo] = 0.0 # Preenche buracos
                
                novos_registros.append(novo_atleta)
                nomes_existentes.add(nome_atleta) # Adiciona ao set para evitar duplicata no próprio arquivo
                recuperados += 1

    # 4. Salva no Banco
    if novos_registros:
        collection.insert_many(novos_registros)
        print(f"✅ SUCESSO! {recuperados} atletas antigos foram recuperados e corrigidos.")
    else:
        print("⚠️ Nenhum atleta novo para restaurar (todos já existem no banco ou arquivo inválido).")

if __name__ == "__main__":
    restaurar_inteligente()