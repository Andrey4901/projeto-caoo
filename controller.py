from model import SistemaModel
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from datetime import datetime # Importação necessária para lidar com datas

class Controller:
    def __init__(self):
        self.model = SistemaModel()

    # -------- Utilitários (Novo) --------
    def _padronizar_data(self, data_str):
        """
        Tenta converter a data de string para o padrão DD/MM/AAAA.
        Aceita: YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY.
        Retorna a string formatada ou None se for inválida.
        """
        if not data_str or pd.isna(data_str) or data_str == "None":
            return None
        
        data_str = str(data_str).strip()
        
        # Lista de formatos que o sistema aceita na entrada
        formatos_aceitos = [
            "%Y-%m-%d", # Ex: 2004-03-27
            "%d-%m-%Y", # Ex: 27-03-2004
            "%d/%m/%Y", # Ex: 27/03/2004
            "%Y/%m/%d"  # Ex: 2004/03/27
        ]

        for fmt in formatos_aceitos:
            try:
                data_obj = datetime.strptime(data_str, fmt)
                # Retorna sempre bonitinho: DD/MM/AAAA
                return data_obj.strftime("%d/%m/%Y")
            except ValueError:
                continue
        
        return None # Não conseguiu converter em nenhum formato

    # -------- Jogadores --------
    def cadastrar_jogador(self, nome, nascimento, peso, estatura, flexibilidade, abdominal, arremesso, salto_h, salto_v):
        # 1. Valida a Data
        data_formatada = self._padronizar_data(nascimento)
        
        if data_formatada is None:
            # Retorna um código específico para erro de data
            return "erro_data"

        try:
            # 2. Cria o dicionário de dados
            novo_jogador = {
                "Nome": nome,
                "Data nasc": data_formatada, # Salva já padronizado
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
            # Erro de conversão numérica
            return "erro_numerico"

    def listar_jogadores(self):
        jogadores = self.model.listar_jogadores()
        
        # Cria uma cópia da lista para não alterar o banco de dados original permanentemente
        # mas garantir que na tela apareça padronizado
        lista_visual = []
        for j in jogadores:
            jogador_temp = j.copy()
            # Padroniza a data existente para exibição
            data_fix = self._padronizar_data(j.get("Data nasc"))
            # Se não tiver data ou for inválida, coloca um traço, senão põe a data formatada
            jogador_temp["Data nasc"] = data_fix if data_fix else "-"
            lista_visual.append(jogador_temp)
            
        return lista_visual

    # -------- Machine Learning --------
    def analisar_perfis_kmeans(self, k=3):
        # ... (Seu código do K-means continua igual aqui) ...
        # Apenas garanta que o método obter_dados_para_ml do model trate possíveis erros de data se necessário
        # mas como usamos dropna, ele vai ignorar datas ruins
        dados_df = self.model.obter_dados_para_ml()

        if dados_df is None or dados_df.empty:
            return None 

        dados_numericos = dados_df.drop('Nome', axis=1)
        scaler = StandardScaler()
        dados_padronizados = scaler.fit_transform(dados_numericos)
        kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
        kmeans.fit(dados_padronizados)
        dados_df['Perfil'] = kmeans.labels_

        return dados_df