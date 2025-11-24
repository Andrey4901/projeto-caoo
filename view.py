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
        
        # ATENÇÃO: Aqui adicionamos uma função para carregar a lista antes de mostrar a tela
        tk.Button(botoes_frame, text="Listar Jogadores", width=20,
                  command=self.exibir_lista_jogadores).pack(side="left", padx=10)
        
        tk.Button(botoes_frame, text="Analisar Perfis (K-Means)", width=20,
                  command=self.exibir_analise_kmeans).pack(side="left", padx=10)

        tk.Button(botoes_frame, text="Sair", width=20,
                  command=self.root.destroy).pack(pady=20)
        
    def tela_cadastro_jogador(self):
        frame = self.frames["cadastro_jogador"]
        
        # Título
        tk.Label(frame, text="Cadastrar Novo Jogador", bg="#222", fg="white", font=("Arial", 16)).pack(pady=20)

        # Container central para alinhar os campos
        container = tk.Frame(frame, bg="#222")
        container.pack(pady=10)

        # Dicionário para guardar as entradas de texto
        self.entries_cadastro = {}

        # Lista de campos atualizada
        # Adicionei "Data de Nascimento" logo após o Nome
        campos = [
            ("Nome:", "nome"),
            ("Data de Nascimento:", "nascimento"),
            ("Peso (kg):", "peso"),
            ("Estatura (cm):", "estatura"),
            ("Flexibilidade (cm):", "flexibilidade"),
            ("Abdominal (rep):", "abdominal"),
            ("Arremesso (m):", "arremesso"),
            ("Salto Horizontal (cm):", "salto_h"),
            ("Salto Vertical (cm):", "salto_v")
        ]

        for i, (texto, chave) in enumerate(campos):
            # Cria o Label
            lbl = tk.Label(container, text=texto, bg="#cccccc", fg="black", width=25, anchor="e", font=("Arial", 10, "bold"))
            lbl.grid(row=i, column=0, padx=5, pady=5, sticky="e")
            
            # Cria o Entry (Campo de texto)
            entry = tk.Entry(container, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            
            # Guarda a referência
            self.entries_cadastro[chave] = entry

        # Botões do rodapé
        botoes_frame = tk.Frame(frame, bg="#222")
        botoes_frame.pack(pady=30)

        tk.Button(botoes_frame, text="Voltar", width=12, bg="#ddd", 
                  command=lambda: self.mostrar_frame("menu_jogadores")).pack(side="left", padx=20)
        
        tk.Button(botoes_frame, text="Cadastrar", width=12, bg="#ddd", 
                  command=self.salvar_novo_jogador).pack(side="left", padx=20)

    def salvar_novo_jogador(self):
        # Pega os valores dos campos
        dados = {k: v.get() for k, v in self.entries_cadastro.items()}
        
        # Verifica se nome ou data estão vazios
        if not dados["nome"] or not dados["nascimento"]:
            messagebox.showwarning("Atenção", "Os campos Nome e Data de Nascimento são obrigatórios.")
            return

        # Chama o controller
        resultado = self.controller.cadastrar_jogador(
            dados["nome"], 
            dados["nascimento"], 
            dados["peso"], 
            dados["estatura"], 
            dados["flexibilidade"], 
            dados["abdominal"], 
            dados["arremesso"], 
            dados["salto_h"], 
            dados["salto_v"]
        )

        # Verifica o resultado
        if resultado == "sucesso":
            messagebox.showinfo("Sucesso", "Jogador cadastrado com sucesso!")
            # Limpa os campos
            for entry in self.entries_cadastro.values():
                entry.delete(0, tk.END)
            self.exibir_lista_jogadores() 
            
        elif resultado == "erro_data":
            messagebox.showerror("Data Inválida", "Formato de data incorreto.\nUse: DD/MM/AAAA (Ex: 25/12/2000)")
            
        elif resultado == "erro_numerico":
            messagebox.showerror("Erro nos Valores", "Verifique se os campos de medidas contêm apenas números.\nUse ponto (.) para decimais.")
    
    def tela_listar_jogadores(self):
        frame = self.frames["listar_jogadores"]
        tk.Label(frame, text="Base de Dados de Jogadores", bg="#222", fg="white", font=("Arial", 16)).pack(pady=10)

        # Frame para a tabela e scrollbar
        tree_frame = tk.Frame(frame)
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

        scroll = ttk.Scrollbar(tree_frame)
        scroll.pack(side="right", fill="y")

        # Tabela
        self.tree_lista = ttk.Treeview(tree_frame, yscrollcommand=scroll.set, selectmode="browse")
        self.tree_lista.pack(fill="both", expand=True)
        scroll.config(command=self.tree_lista.yview)

        tk.Button(frame, text="Voltar", width=12, command=lambda: self.mostrar_frame("menu_jogadores")).pack(pady=10)

    def exibir_lista_jogadores(self):
        # Pega a lista atualizada do controller
        jogadores = self.controller.listar_jogadores()
        
        # Limpa a tabela atual
        for i in self.tree_lista.get_children():
            self.tree_lista.delete(i)

        if not jogadores:
            self.mostrar_frame("listar_jogadores")
            return

        # Define as colunas dinamicamente com base no primeiro jogador
        # (Isso garante que se adicionarmos novos campos no futuro, a tabela se adapta)
        colunas = list(jogadores[0].keys())
        self.tree_lista['columns'] = colunas
        
        # Formata a coluna fantasma do Tkinter
        self.tree_lista.column("#0", width=0, stretch=tk.NO)
        self.tree_lista.heading("#0", text="", anchor=tk.CENTER)

        # Formata os cabeçalhos
        for col in colunas:
            self.tree_lista.column(col, anchor=tk.CENTER, width=90)
            self.tree_lista.heading(col, text=col, anchor=tk.CENTER)

        # Insere os dados
        for i, jogador in enumerate(jogadores):
            valores = list(jogador.values())
            self.tree_lista.insert(parent="", index="end", iid=i, text="", values=valores)

        self.mostrar_frame("listar_jogadores")

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