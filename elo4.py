from elo import Elo
import numpy as np

class Elo_04(Elo):
    def proc(self, data):
        """
        Recebe: Dicionário com dados normalizados
        Faz: Compara com o banco de dados (Centróides) e define a Posição
        """
        # Acessa o model que foi passado no __init__ lá no Controller
        df_ref = self.model.obter_perfis_referencia()
        
        atleta_norm = data['vetor_norm']
        
        menor_distancia = float('inf')
        melhor_posicao = "Indefinido"
        
        atributos = ['peso', 'estatura', 'flexibilidade', 'abdominal', 'arremesso', 'Salto horizontal', 'Salto vertical']
        maximos = np.array([130.0, 210.0, 100.0, 100.0, 30.0, 250.0, 100.0])

        # Algoritmo de Distância (O mesmo que usávamos no controller)
        for index, row in df_ref.iterrows():
            valores_ref = np.array([row[k] for k in atributos])
            ref_norm = valores_ref / maximos
            
            distancia = np.linalg.norm(atleta_norm - ref_norm)
            
            if distancia < menor_distancia:
                menor_distancia = distancia
                melhor_posicao = row['Posicao']

        # Adiciona a decisão final ao pacote de dados
        data['melhor_posicao'] = melhor_posicao
        
        return data