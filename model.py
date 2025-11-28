import pandas as pd
from pymongo import MongoClient

class SistemaModel:
    def __init__(self):
        # Conexão MongoDB
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["sistema_atletas"]
        self.collection = self.db["jogadores"]

    def cadastrar_jogador(self, dados_jogador):
        try:
            self.collection.insert_one(dados_jogador)
            return True
        except Exception as e:
            print(f"Erro ao salvar: {e}")
            return False

    def listar_jogadores(self):
        try:
            return list(self.collection.find({}, {'_id': 0}))
        except Exception:
            return []

    def excluir_jogador(self, nome_jogador):
        try:
            # Tenta apagar por Nome (Maiúsculo ou minúsculo)
            res = self.collection.delete_one({"Nome": nome_jogador})
            if res.deleted_count == 0:
                self.collection.delete_one({"nome": nome_jogador})
            return True
        except:
            return False

    def obter_dados_para_ml(self):
        """
        Versão BLINDADA: Filtra dados ruins e padroniza chaves.
        """
        # Pega tudo do banco
        dados_brutos = list(self.collection.find({}, {'_id': 0}))
        
        dados_limpos = []
        
        for d in dados_brutos:
            novo_d = d.copy()
            
            # 1. Correção de chaves (nome -> Nome)
            # Se não tem "Nome" mas tem "nome", a gente arruma
            if "Nome" not in novo_d and "nome" in novo_d:
                novo_d["Nome"] = novo_d.pop("nome")
            
            # 2. Verificação de Integridade
            # Só aceita se tiver "Nome" e "peso" (campos mínimos)
            if "Nome" in novo_d and ("peso" in novo_d or "Peso" in novo_d):
                dados_limpos.append(novo_d)

        if not dados_limpos:
            return None
            
        df = pd.DataFrame(dados_limpos)
        
        # 3. Conversão Numérica
        cols_numericas = ['peso', 'estatura', 'flexibilidade', 'abdominal', 'arremesso', 'Salto horizontal', 'Salto vertical']
        
        # Garante que as colunas existem no DataFrame, mesmo que vazias, para não dar erro
        for col in cols_numericas:
            if col not in df.columns:
                df[col] = 0 # Preenche com 0 se a coluna nem existir
        
        for col in cols_numericas:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 4. Remove quem tem NaN nas colunas numéricas essenciais
        df.dropna(subset=cols_numericas, inplace=True)
        
        # 5. Remove quem ficou com Nome vazio ou "nan"
        df = df[df['Nome'].notna()]
        df = df[df['Nome'] != ""]
        
        return df

    def obter_perfis_referencia(self):
        # ... (Mantenha o seu código de perfis de referência igual estava) ...
        perfis = [
            {"Nome": "REF: Goleiro", "Posicao": "Goleiro", "peso": 88.0, "estatura": 198.0, "flexibilidade": 70.0, "abdominal": 55.0, "arremesso": 5.0, "Salto horizontal": 180.0, "Salto vertical": 70.0},
            {"Nome": "REF: Lateral", "Posicao": "Lateral", "peso": 85.0, "estatura": 185.0, "flexibilidade": 55.0, "abdominal": 60.0, "arremesso": 7.5, "Salto horizontal": 210.0, "Salto vertical": 50.0},
            {"Nome": "REF: Zagueiro", "Posicao": "Zagueiro", "peso": 100.0, "estatura": 192.0, "flexibilidade": 60.0, "abdominal": 70.0, "arremesso": 8.5, "Salto horizontal": 190.0, "Salto vertical": 55.0},
            {"Nome": "REF: Ponta", "Posicao": "Ponta", "peso": 75.0, "estatura": 175.0, "flexibilidade": 65.0, "abdominal": 50.0, "arremesso": 7.0, "Salto horizontal": 230.0, "Salto vertical": 45.0},
            {"Nome": "REF: Centroavante", "Posicao": "Centroavante", "peso": 115.0, "estatura": 200.0, "flexibilidade": 50.0, "abdominal": 55.0, "arremesso": 10.0, "Salto horizontal": 160.0, "Salto vertical": 60.0}
        ]
        return pd.DataFrame(perfis)