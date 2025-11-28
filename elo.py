from abc import ABC, abstractmethod

class Elo(ABC):
    def __init__(self, model):
        self.model = model
        self.next = None

    def set_next(self, next):
        self.next = next
        return next # Retorno o next para facilitar o encadeamento se quiser

    @abstractmethod
    def proc(self, data):
        pass

    def run(self, data):
        # Processa o dado no elo atual
        data = self.proc(data)

        # Se houver erro ou interrupção, podemos retornar None ou tratar aqui
        if data is None:
            return None

        # Passa para o próximo
        if self.next is not None:
            return self.next.run(data)
        else:
            return data