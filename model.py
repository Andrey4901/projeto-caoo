import json, os
import pandas as pd

class SistemaModel:
    def __init__(self):
        self.jogadores = []
        self.carregar_jogadores()


    def obter_dados_para_ml(self):
        """
        Prepara os dados dos jogadores para serem usados em algoritmos de ML.
        - Remove jogadores com dados ausentes.
        - Retorna um DataFrame apenas com os dados numéricos e os nomes.
        """
        if not self.jogadores:
            return None

        # Corrige as chaves com espaços em branco (ex: "Nome " -> "Nome")
        jogadores_corrigidos = [{k.strip(): v for k, v in jogador.items()} for jogador in self.jogadores]

        # Converte para DataFrame do Pandas
        df = pd.DataFrame(jogadores_corrigidos)

        # Remove linhas que tenham QUALQUER valor nulo/ausente
        df.dropna(inplace=True)

        # Seleciona apenas as colunas que vamos usar para a análise
        # Garante que as colunas existem antes de tentar usá-las
        colunas_numericas = ['peso', 'estatura', 'flexibilidade', 'abdominal', 'arremesso', 'Salto horizontal', 'Salto vertical']
        colunas_disponiveis = [col for col in colunas_numericas if col in df.columns]

        if not colunas_disponiveis:
             return None # Não há dados suficientes

        # Retorna o DataFrame com nomes e os dados numéricos limpos
        return df[['Nome'] + colunas_disponiveis]

    # ---------------- Jogadores ----------------
    def cadastrar_jogador(self, dados):
        self.jogadores.append(dados)
        self.salvar_jogadores()
        return True

    def listar_jogadores(self):
        return self.jogadores

    def salvar_jogadores(self):
        with open("jogadores.json", "w", encoding="utf-8") as f:
            json.dump(self.jogadores, f, indent=4, ensure_ascii=False)

    def carregar_jogadores(self):
        if os.path.exists("jogadores.json"):
            with open("jogadores.json", "r", encoding="utf-8") as f:
                self.jogadores = json.load(f)