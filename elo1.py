from elo import Elo

class Elo_01(Elo):
    def proc(self, data):
        """
        Recebe: Lista bruta da Treeview ['Nome', 'Data', '85.0', ...]
        Retorna: Dicionário {'Nome': '...', 'peso': 85.0, ...}
        """
        raw_list = data # A entrada é a lista

        try:
            # Função auxiliar para limpar números
            def safe_float(val):
                if val in ['-', 'None', 'nan', None]: return 0.0
                return float(val)

            # Monta o dicionário inicial
            atleta_dict = {
                "Nome": raw_list[0],
                "Data nasc": raw_list[1],
                "peso": safe_float(raw_list[2]),
                "estatura": safe_float(raw_list[3]),
                "flexibilidade": safe_float(raw_list[4]),
                "abdominal": safe_float(raw_list[5]),
                "arremesso": safe_float(raw_list[6]),
                "Salto horizontal": safe_float(raw_list[7]),
                "Salto vertical": safe_float(raw_list[8]),
            }
            
            return atleta_dict

        except Exception as e:
            print(f"Erro no Elo 1: {e}")
            return None