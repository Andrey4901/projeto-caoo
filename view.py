import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

class SistemaView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        
        # Configuração da janela principal
        self.root.title("Sistema de Análise de Atletas")
        self.root.geometry("800x600")
        self.root.configure(bg="#222")

        # Define os frames que AINDA vamos usar
        self.frames = {}
        for nome in ["menu_jogadores", "cadastro_jogador", "listar_jogadores", "analise_kmeans"]:
            frame = tk.Frame(root, bg="#222")
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.frames[nome] = frame

        # Cria as telas
        self.tela_menu_jogadores()
        self.tela_cadastro_jogador()
        self.tela_listar_jogadores()
        self.tela_analise_kmeans()

        # Define a tela inicial diretamente como o menu de jogadores
        self.mostrar_frame("menu_jogadores")

    def mostrar_frame(self, nome):
        self.frames[nome].tkraise()

    # -------- Menu de jogadores --------
    def tela_menu_jogadores(self):
        frame = self.frames["menu_jogadores"]
        tk.Label(frame, text="Menu de Jogadores", bg="#222", fg="white", font=("Arial", 16)).pack(pady=20)

        botoes_frame = tk.Frame(frame, bg="#222")
        botoes_frame.pack(pady=20)

        tk.Button(botoes_frame, text="Cadastrar Jogador", width=20,
                  command=lambda: self.mostrar_frame("cadastro_jogador")).pack(side="left", padx=10)
        tk.Button(botoes_frame, text="Listar Jogadores", width=20,
                  command=lambda: self.mostrar_frame("listar_jogadores")).pack(side="left", padx=10)
        
        tk.Button(botoes_frame, text="Analisar Perfis (K-Means)", width=20,
                  command=self.exibir_analise_kmeans).pack(side="left", padx=10)

        # O botão Sair agora fecha o aplicativo
        tk.Button(botoes_frame, text="Sair", width=20,
                  command=self.root.destroy).pack(pady=20)
        
    def tela_cadastro_jogador(self):
        frame = self.frames["cadastro_jogador"]
        tk.Label(frame, text="Cadastro de Jogador (Em desenvolvimento)", bg="#222", fg="white", font=("Arial", 14)).pack(pady=50)
        tk.Button(frame, text="Voltar", width=12, command=lambda: self.mostrar_frame("menu_jogadores")).pack(pady=10)

    def tela_listar_jogadores(self):
        frame = self.frames["listar_jogadores"]
        tk.Label(frame, text="Listagem de Jogadores (Em desenvolvimento)", bg="#222", fg="white", font=("Arial", 14)).pack(pady=50)
        tk.Button(frame, text="Voltar", width=12, command=lambda: self.mostrar_frame("menu_jogadores")).pack(pady=10)

    # -------- Telas de Análise (NOVA SEÇÃO) --------
    def tela_analise_kmeans(self):
        frame = self.frames["analise_kmeans"]
        tk.Label(frame, text="Análise de Perfis de Jogadores (K-Means)", bg="#222", fg="white", font=("Arial", 16)).pack(pady=10)

        # Frame para a tabela
        tree_frame = tk.Frame(frame)
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Scrollbar
        scroll = ttk.Scrollbar(tree_frame)
        scroll.pack(side="right", fill="y")

        # O Treeview é a nossa tabela
        self.tree_kmeans = ttk.Treeview(tree_frame, yscrollcommand=scroll.set, selectmode="extended")
        self.tree_kmeans.pack(fill="both", expand=True)
        scroll.config(command=self.tree_kmeans.yview)

        tk.Button(frame, text="Voltar", width=12, command=lambda: self.mostrar_frame("menu_jogadores")).pack(pady=10)


    def exibir_analise_kmeans(self):
        # Chama o controller para obter os dados analisados
        resultados_df = self.controller.analisar_perfis_kmeans()

        if resultados_df is None:
            messagebox.showwarning("Atenção", "Não há dados suficientes ou válidos para realizar a análise.")
            return
        
        # Limpa a tabela antiga
        for i in self.tree_kmeans.get_children():
            self.tree_kmeans.delete(i)

        # Define as colunas da tabela
        self.tree_kmeans['columns'] = list(resultados_df.columns)
        self.tree_kmeans.column("#0", width=0, stretch=tk.NO)
        self.tree_kmeans.heading("#0", text="", anchor=tk.CENTER)

        for col in self.tree_kmeans['columns']:
            self.tree_kmeans.column(col, anchor=tk.CENTER, width=80)
            self.tree_kmeans.heading(col, text=col, anchor=tk.CENTER)
        
        # Adiciona os dados na tabela
        for index, row in resultados_df.iterrows():
            self.tree_kmeans.insert(parent="", index="end", iid=index, text="", values=list(row))
            
        # Mostra a tela com os resultados
        self.mostrar_frame("analise_kmeans")