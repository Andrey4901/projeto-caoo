from elo import Elo
import numpy as np

class Elo_03(Elo):
    def proc(self, data):
        """
        Recebe: Dicionário do atleta
        Faz: Normaliza os dados (0 a 1) para o gráfico
        Retorna: Dicionário com chave 'dados_grafico' e 'vetor_norm'
        """
        atributos = ['peso', 'estatura', 'flexibilidade', 'abdominal', 'arremesso', 'Salto horizontal', 'Salto vertical']
        
        # Valores máximos teóricos para normalização
        maximos = np.array([130.0, 210.0, 100.0, 100.0, 30.0, 250.0, 100.0])
        
        # Cria vetor numpy dos dados do atleta
        valores_atleta = np.array([data[k] for k in atributos])
        
        # Divide para achar a porcentagem (Normalização)
        atleta_norm = valores_atleta / maximos

        # Salva no dicionário para o próximo elo usar
        data['vetor_norm'] = atleta_norm
        
        # Prepara estrutura para o View (Gráfico)
        data['dados_grafico'] = {
            "labels": ["Peso", "Estatura", "Flex.", "Abd.", "Arremesso", "S. Horiz.", "S. Vert."],
            "values_atleta": list(atleta_norm),
            "values_original": list(valores_atleta)
        }

        return data