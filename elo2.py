from elo import Elo
from datetime import datetime

class Elo_02(Elo):
    def proc(self, data):
        """
        Recebe: Dicionário do atleta
        Faz: Calcula a idade
        Retorna: Dicionário atualizado
        """
        try:
            data_nasc_str = data["Data nasc"]
            idade = "??"
            
            # Tenta calcular a idade
            try:
                nasc = datetime.strptime(data_nasc_str, "%d/%m/%Y")
                hoje = datetime.now()
                idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
            except:
                pass # Se der erro na data, mantém ??

            # Adiciona o campo novo formatado
            data["Data_formatada"] = f"{data_nasc_str} ({idade} anos)"
            
            return data

        except Exception as e:
            print(f"Erro no Elo 2: {e}")
            return data # Retorna o dado mesmo se falhar o cálculo de idade