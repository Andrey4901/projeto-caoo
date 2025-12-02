from model import SistemaModel
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from datetime import datetime

from elo1 import Elo_01
from elo2 import Elo_02
from elo3 import Elo_03
from elo4 import Elo_04

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
        
    def excluir_jogador(self, nome):
        return self.model.excluir_jogador(nome)

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
        # 1. Obter dados
        df_jogadores = self.model.obter_dados_para_ml()
        if df_jogadores is None or df_jogadores.empty:
            return None, "Sem dados de jogadores suficientes."

        # 2. FILTRO DE QUALIDADE
        features = ['peso', 'estatura', 'flexibilidade', 'abdominal', 'arremesso', 'Salto horizontal', 'Salto vertical']
        contagem_zeros = (df_jogadores[features] == 0).sum(axis=1)
        df_jogadores = df_jogadores[contagem_zeros < 3]

        if df_jogadores.empty:
            return None, "Todos os atletas foram filtrados (dados incompletos)."

        # 3. Preparação dos Dados
        df_ref = self.model.obter_perfis_referencia()
        df_jogadores['Tipo'] = 'Atleta'
        df_ref['Tipo'] = 'Referencia'
        
        cols_comuns = ['Nome', 'peso', 'estatura', 'flexibilidade', 'abdominal', 'arremesso', 'Salto horizontal', 'Salto vertical', 'Tipo']
        df_completo = pd.concat([df_jogadores, df_ref], ignore_index=True)
        df_completo = df_completo[cols_comuns]

        # Pegamos os dados brutos numéricos
        X_bruto = df_completo[features].fillna(0).values

        # --- PASSO A: LÓGICA DE CLASSIFICAÇÃO (Quem conecta com quem?) ---
        # Aqui usamos a RÉGUA FIXA (Absoluta).
        # Isso garante que o Diogo (116kg) seja matematicamente puxado para o Centroavante.
        maximos = np.array([130.0, 210.0, 100.0, 100.0, 30.0, 250.0, 100.0])
        X_logica = X_bruto / maximos

        n_jog = len(df_jogadores)
        clusters = []
        
        # Separa para cálculo de distância
        X_jog_logica = X_logica[:n_jog]
        X_ref_logica = X_logica[n_jog:]
        
        for j in X_jog_logica:
            distancias = np.linalg.norm(X_ref_logica - j, axis=1)
            clusters.append(np.argmin(distancias)) # Define a cor/grupo correto
        
        for i in range(len(X_ref_logica)):
            clusters.append(i)

        df_completo['Cluster'] = clusters

        # --- PASSO B: VISUALIZAÇÃO (Onde o ponto aparece?) ---
        # Aqui usamos a RÉGUA RELATIVA (StandardScaler).
        # Ela é muito melhor para o PCA desenhar gráficos bonitos e espalhados,
        # como na imagem que você gostou.
        scaler_visual = StandardScaler()
        X_visual = scaler_visual.fit_transform(X_bruto)

        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_visual) 
        
        df_completo['PCA1'] = X_pca[:, 0]
        df_completo['PCA2'] = X_pca[:, 1]

        mapa_nomes = {}
        for idx, row in df_ref.iterrows():
            mapa_nomes[idx] = row['Posicao']
            
        return {'df': df_completo, 'mapa_nomes': mapa_nomes}, "sucesso"

    # -------- Lógica de Detalhes e Predição --------
    def obter_detalhes_e_predicao(self, valores_treeview):
        """
        Processa os dados usando o padrão Chain of Responsibility (Elos).
        """
        # 1. Instancia os Elos, passando o model (necessário para o Elo 4)
        elo1 = Elo_01(self.model)
        elo2 = Elo_02(self.model)
        elo3 = Elo_03(self.model)
        elo4 = Elo_04(self.model)

        # 2. Encadeia (Elo 1 -> Elo 2 -> Elo 3 -> Elo 4)
        elo1.set_next(elo2)
        elo2.set_next(elo3)
        elo3.set_next(elo4)

        # 3. Roda a esteira!
        # Passamos a lista bruta e recebemos o pacote completo processado
        resultado_final = elo1.run(valores_treeview)

        if resultado_final is None:
            return None, "Erro no processamento dos elos."

        # 4. Formata o retorno para a View
        # A View espera: dicionário com chaves específicas
        return {
            "atleta": resultado_final, # O dict já contém Nome, Data, etc.
            "melhor_posicao": resultado_final['melhor_posicao'],
            "dados_grafico": resultado_final['dados_grafico']
        }, "sucesso"