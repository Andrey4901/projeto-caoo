from model import SistemaModel
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class Controller:
    def __init__(self):
        self.model = SistemaModel()

    # -------- Jogadores --------
    def cadastrar_jogador(self, dados):
        return self.model.cadastrar_jogador(dados)

    def listar_jogadores(self):
        return self.model.listar_jogadores()
    
     # -------- Machine Learning --------
    def analisar_perfis_kmeans(self, k=3):
        """
        Executa o algoritmo K-Means nos dados dos jogadores.
        """
        # 1. Pega os dados limpos do modelo
        dados_df = self.model.obter_dados_para_ml()

        if dados_df is None or dados_df.empty:
            return None # Retorna None se não houver dados

        # 2. Separa os dados numéricos para o algoritmo
        dados_numericos = dados_df.drop('Nome', axis=1)

        # 3. Padroniza os dados (passo crucial para o K-Means)
        scaler = StandardScaler()
        dados_padronizados = scaler.fit_transform(dados_numericos)

        # 4. Aplica o K-Means
        kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
        kmeans.fit(dados_padronizados)

        # 5. Adiciona os resultados (os clusters) ao DataFrame original
        dados_df['Perfil'] = kmeans.labels_

        return dados_df