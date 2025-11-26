from model import SistemaModel
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from datetime import datetime

class Controller:
    def __init__(self):
        self.model = SistemaModel()

    # -------- Utilitários --------
    def _padronizar_data(self, data_str):
        """
        Padroniza a data para DD/MM/AAAA.
        """
        if not data_str or pd.isna(data_str) or str(data_str) == "None":
            return None
        
        data_str = str(data_str).strip()
        
        # Lista de formatos aceitos
        formatos_aceitos = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"]

        for fmt in formatos_aceitos:
            try:
                data_obj = datetime.strptime(data_str, fmt)
                return data_obj.strftime("%d/%m/%Y")
            except ValueError:
                continue
        return None

    def _calcular_idade(self, data_nasc_str):
        """
        Calcula a idade baseada na string de data.
        """
        try:
            nasc = datetime.strptime(data_nasc_str, "%d/%m/%Y")
            hoje = datetime.now()
            idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
            return idade
        except (ValueError, TypeError):
            return "??"

    def _formatar_numero_visual(self, valor):
        """
        Força o arredondamento para INTEIRO.
        Remove qualquer casa decimal.
        Ex: 110.0 -> "110"
            85.6  -> "86"
        """
        if valor is None or str(valor) in ["None", "", "-", "nan"]:
            return "-"
        try:
            # 1. Converte para float primeiro (garante que lê "110.0" ou 110.0)
            val_float = float(valor)
            # 2. Arredonda matematicamente
            val_round = round(val_float)
            # 3. Converte para INT (remove o .0) e devolve como String
            return str(int(val_round))
        except (ValueError, TypeError):
            # Se não for número, devolve o que veio
            return str(valor)

    # -------- Jogadores --------
    def cadastrar_jogador(self, nome, nascimento, peso, estatura, flexibilidade, abdominal, arremesso, salto_h, salto_v):
        # 1. Valida a Data
        data_formatada = self._padronizar_data(nascimento)
        
        if data_formatada is None:
            return "erro_data"

        try:
            # 2. Cria o dicionário de dados
            novo_jogador = {
                "Nome": nome,
                "Data nasc": data_formatada,
                "peso": float(peso),
                "estatura": float(estatura),
                "flexibilidade": float(flexibilidade),
                "abdominal": float(abdominal),
                "arremesso": float(arremesso),
                "Salto horizontal": float(salto_h),
                "Salto vertical": float(salto_v)
            }
            # Envia para o model salvar
            self.model.cadastrar_jogador(novo_jogador)
            return "sucesso"
        except ValueError:
            return "erro_numerico"

    def listar_jogadores(self):
        jogadores = self.model.listar_jogadores()
        
        lista_visual = []
        
        # Lista explícita de colunas que devem ser INTEIROS
        cols_numericas = [
            'peso', 'estatura', 'flexibilidade', 'abdominal', 
            'arremesso', 'Salto horizontal', 'Salto vertical'
        ]

        for j in jogadores:
            jogador_temp = j.copy()
            
            # 1. Formata Data
            data_fix = self._padronizar_data(j.get("Data nasc"))
            jogador_temp["Data nasc"] = data_fix if data_fix else "-"
            
            # 2. Arredonda Números (Aplica a formatação agressiva)
            for col in cols_numericas:
                val = j.get(col)
                jogador_temp[col] = self._formatar_numero_visual(val)

            lista_visual.append(jogador_temp)
            
        return lista_visual

    # -------- Machine Learning e Gráfico --------
    def gerar_analise_grafica(self):
        # 1. Pega dados
        df_jogadores = self.model.obter_dados_para_ml()
        if df_jogadores is None or df_jogadores.empty:
            return None, "Sem dados de jogadores suficientes."

        # 2. Pega dados de referência
        df_ref = self.model.obter_perfis_referencia()

        # 3. Junta tudo
        df_jogadores['Tipo'] = 'Atleta'
        df_ref['Tipo'] = 'Referencia'
        
        cols_comuns = ['Nome', 'peso', 'estatura', 'flexibilidade', 'abdominal', 'arremesso', 'Salto horizontal', 'Salto vertical', 'Tipo']
        df_completo = pd.concat([df_jogadores, df_ref], ignore_index=True)
        df_completo = df_completo[cols_comuns]

        # 4. K-Means
        features = ['peso', 'estatura', 'flexibilidade', 'abdominal', 'arremesso', 'Salto horizontal', 'Salto vertical']
        X = df_completo[features]
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        kmeans = KMeans(n_clusters=5, n_init=10, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        df_completo['Cluster'] = clusters

        # 5. PCA
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        
        df_completo['PCA1'] = X_pca[:, 0]
        df_completo['PCA2'] = X_pca[:, 1]

        return df_completo, "sucesso"

    # -------- Lógica de Detalhes e Predição --------
    def obter_detalhes_e_predicao(self, valores_treeview):
        try:
            # 1. Converter dados da View (Strings) para Números e Dicionário
            atleta = {
                "Nome": valores_treeview[0],
                "Data nasc": valores_treeview[1],
                "peso": float(valores_treeview[2]) if valores_treeview[2] != 'None' and valores_treeview[2] != '-' else 0,
                "estatura": float(valores_treeview[3]) if valores_treeview[3] != 'None' and valores_treeview[3] != '-' else 0,
                "flexibilidade": float(valores_treeview[4]) if valores_treeview[4] != 'None' and valores_treeview[4] != '-' else 0,
                "abdominal": float(valores_treeview[5]) if valores_treeview[5] != 'None' and valores_treeview[5] != '-' else 0,
                "arremesso": float(valores_treeview[6]) if valores_treeview[6] != 'None' and valores_treeview[6] != '-' else 0,
                "Salto horizontal": float(valores_treeview[7]) if valores_treeview[7] != 'None' and valores_treeview[7] != '-' else 0,
                "Salto vertical": float(valores_treeview[8]) if valores_treeview[8] != 'None' and valores_treeview[8] != '-' else 0,
            }
            
            # Adiciona a idade
            idade = self._calcular_idade(atleta["Data nasc"])
            atleta["Data_formatada"] = f"{atleta['Data nasc']} ({idade} anos)"

        except ValueError:
            return None, "Erro ao converter dados numéricos."

        # 2. Obter as referências
        df_ref = self.model.obter_perfis_referencia()
        
        # 3. Descobrir qual posição é a mais próxima
        menor_distancia = float('inf')
        melhor_posicao = "Indefinido"
        
        atributos = ['peso', 'estatura', 'flexibilidade', 'abdominal', 'arremesso', 'Salto horizontal', 'Salto vertical']
        
        valores_atleta = np.array([atleta[k] for k in atributos])
        maximos = np.array([130.0, 210.0, 100.0, 100.0, 30.0, 250.0, 100.0]) 
        atleta_norm = valores_atleta / maximos

        for index, row in df_ref.iterrows():
            valores_ref = np.array([row[k] for k in atributos])
            ref_norm = valores_ref / maximos
            distancia = np.linalg.norm(atleta_norm - ref_norm)
            
            if distancia < menor_distancia:
                menor_distancia = distancia
                melhor_posicao = row['Posicao']

        # 4. Preparar dados para o Gráfico
        dados_grafico = {
            "labels": ["Peso", "Estatura", "Flex.", "Abd.", "Arremesso", "S. Horiz.", "S. Vert."],
            "values_atleta": list(atleta_norm),
            "values_original": list(valores_atleta)
        }

        return {
            "atleta": atleta,
            "melhor_posicao": melhor_posicao,
            "dados_grafico": dados_grafico
        }, "sucesso"