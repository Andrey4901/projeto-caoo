import json, os
import pandas as pd

class SistemaModel:
    def __init__(self):
        self.jogadores = []
        self.carregar_jogadores()
    
    def obter_perfis_referencia(self):
        """
        Retorna os dados 'ideais' para cada posição no Polo Aquático.
        """
        perfis = [
            {"Nome": "REF: Goleiro", "Posicao": "Goleiro", "peso": 92.0, "estatura": 193.0, "flexibilidade": 65.0, "abdominal": 50.0, "arremesso": 6.0, "Salto horizontal": 190.0, "Salto vertical": 55.0},
            {"Nome": "REF: Lateral", "Posicao": "Lateral", "peso": 82.0, "estatura": 182.0, "flexibilidade": 55.0, "abdominal": 40.0, "arremesso": 6.5, "Salto horizontal": 185.0, "Salto vertical": 45.0},
            {"Nome": "REF: Zagueiro", "Posicao": "Zagueiro", "peso": 98.0, "estatura": 190.0, "flexibilidade": 70.0, "abdominal": 50.0, "arremesso": 7.5, "Salto horizontal": 195.0, "Salto vertical": 50.0},
            {"Nome": "REF: Ponta", "Posicao": "Ponta", "peso": 78.0, "estatura": 178.0, "flexibilidade": 60.0, "abdominal": 48.0, "arremesso": 7.0, "Salto horizontal": 180.0, "Salto vertical": 48.0},
            {"Nome": "REF: Centroavante", "Posicao": "Centroavante", "peso": 105.0, "estatura": 195.0, "flexibilidade": 60.0, "abdominal": 45.0, "arremesso": 8.0, "Salto horizontal": 175.0, "Salto vertical": 52.0}
        ]
        return pd.DataFrame(perfis)
    
    def obter_dados_para_ml(self):
        # ... (seu código anterior do obter_dados_para_ml) ...
        # Apenas certifique-se de que ele está funcionando como fizemos antes
        if not self.jogadores:
            return None
        
        # Correção rápida para garantir chaves limpas
        jogadores_corrigidos = [{k.strip(): v for k, v in jogador.items()} for jogador in self.jogadores]
        df = pd.DataFrame(jogadores_corrigidos)
        
        # Converte colunas numéricas (importante caso venham como string)
        cols_numericas = ['peso', 'estatura', 'flexibilidade', 'abdominal', 'arremesso', 'Salto horizontal', 'Salto vertical']
        for col in cols_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.dropna(subset=cols_numericas, inplace=True)
        return df[['Nome', 'Data nasc'] + [c for c in cols_numericas if c in df.columns]]

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