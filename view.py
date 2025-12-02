import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

class SistemaView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        
        # Configuração da janela principal
        self.root.title("Sistema de Análise de Atletas")
        self.root.geometry("800x600")
        self.root.configure(bg="#222")
        self.root.protocol("WM_DELETE_WINDOW", self.fechar_sistema)

        # Define os frames que AINDA vamos usar
        self.frames = {}
        for nome in ["menu_jogadores", "cadastro_jogador", "listar_jogadores", "analise_kmeans", "detalhes_jogador"]:
            frame = tk.Frame(root, bg="#222")
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.frames[nome] = frame
        
        # ... (suas chamadas de telas) ...
        self.tela_menu_jogadores()
        self.tela_cadastro_jogador()
        self.tela_listar_jogadores()
        self.tela_analise_kmeans()
        self.tela_detalhes_jogador() # <--- Adicione a chamada para criar a nova tela vazia

        self.mostrar_frame("menu_jogadores")

    def fechar_sistema(self):
        """Fecha a janela e mata o processo Python para evitar travamento no VS Code."""
        try:
            self.root.quit()    # Para o mainloop
            self.root.destroy() # Destroi a janela
            print("Sistema encerrado corretamente.")
        except Exception:
            pass

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
                  command=self.fechar_sistema).pack(pady=20)
        
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

    def remover_jogador_selecionado(self):
        # 1. Verifica se tem alguém selecionado
        item_selecionado = self.tree_lista.selection()
        
        if not item_selecionado:
            messagebox.showwarning("Atenção", "Selecione um jogador na lista para remover.")
            return

        # 2. Pega o nome do jogador (primeira coluna)
        valores = self.tree_lista.item(item_selecionado, "values")
        nome_alvo = valores[0] 

        # 3. Pede confirmação (Segurança)
        resposta = messagebox.askyesno("Confirmar Exclusão", 
                                       f"Tem certeza que deseja apagar '{nome_alvo}' permanentemente?\nEssa ação não pode ser desfeita.")
        
        if resposta:
            # 4. Chama o controller para apagar do MongoDB
            sucesso = self.controller.excluir_jogador(nome_alvo)
            
            if sucesso:
                messagebox.showinfo("Sucesso", f"O registro de '{nome_alvo}' foi apagado.")
                # 5. Atualiza a lista na hora
                self.exibir_lista_jogadores()
            else:
                messagebox.showerror("Erro", "Não foi possível remover o jogador do banco de dados.")
    
    def tela_listar_jogadores(self):
        frame = self.frames["listar_jogadores"]
        
        # Limpa o frame antes de recriar (para evitar duplicar botões se voltar na tela)
        for widget in frame.winfo_children():
            widget.destroy()

        tk.Label(frame, text="Base de Dados de Jogadores", bg="#222", fg="white", font=("Arial", 16)).pack(pady=10)

        # Frame para a tabela
        tree_frame = tk.Frame(frame)
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

        scroll = ttk.Scrollbar(tree_frame)
        scroll.pack(side="right", fill="y")

        self.tree_lista = ttk.Treeview(tree_frame, yscrollcommand=scroll.set, selectmode="browse")
        self.tree_lista.pack(fill="both", expand=True)
        scroll.config(command=self.tree_lista.yview)

        # --- ÁREA DOS BOTÕES (RODAPÉ) ---
        botoes_frame = tk.Frame(frame, bg="#222")
        botoes_frame.pack(pady=15)

        # Botão Voltar
        tk.Button(botoes_frame, text="Voltar", width=12, 
                  command=lambda: self.mostrar_frame("menu_jogadores")).pack(side="left", padx=10)
        
        # Botão Remover (Vermelho) - NOVO!
        tk.Button(botoes_frame, text="Remover", width=12, bg="#d9534f", fg="white",
                  command=self.remover_jogador_selecionado).pack(side="left", padx=10)

        # Botão Selecionar (Verde)
        tk.Button(botoes_frame, text="Selecionar", width=12, bg="#4CAF50", fg="white",
                  command=self.selecionar_jogador_da_lista).pack(side="left", padx=10)

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
        
        # 1. Título (Topo)
        tk.Label(frame, text="Mapa de Perfis (Clusters)", bg="#222", fg="white", font=("Arial", 16)).pack(side="top", pady=10)

        # 2. Botões (Rodapé)
        # IMPORTANTE: Empacotamos com side="bottom" ANTES do gráfico.
        # Assim, eles garantem seu lugar no chão da janela.
        botoes_frame = tk.Frame(frame, bg="#222")
        botoes_frame.pack(side="bottom", fill="x", pady=15)
        
        # Centralizando os botões usando um container interno ou pack simples
        container_botoes = tk.Frame(botoes_frame, bg="#222")
        container_botoes.pack()

        tk.Button(container_botoes, text="Atualizar Gráfico", width=15, height=2, bg="#ddd",
                  command=self.exibir_analise_kmeans).pack(side="left", padx=10)
        
        tk.Button(container_botoes, text="Voltar", width=15, height=2, bg="#ddd",
                  command=lambda: self.mostrar_frame("menu_jogadores")).pack(side="left", padx=10)

        # 3. Área do Gráfico (Recheio)
        # Agora sim, mandamos ele ocupar "o que sobrou" (expand=True)
        self.frame_grafico = tk.Frame(frame, bg="white") 
        self.frame_grafico.pack(side="top", fill="both", expand=True, padx=10, pady=5)

    def exibir_analise_kmeans(self):
        self.mostrar_frame("analise_kmeans")
        
        # Limpa o gráfico antigo
        for w in self.frame_grafico.winfo_children(): w.destroy()

        res, msg = self.controller.gerar_analise_grafica()
        if res is None: 
            return tk.Label(self.frame_grafico, text=f"Erro: {msg}", bg="white", fg="red").pack(pady=50)

        df, mapa = res['df'], res['mapa_nomes']

        try:
            fig, ax = plt.subplots(figsize=(9, 6), dpi=100)
            
            # Cores vibrantes e distintas
            cores = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']
            
            at = df[df['Tipo'] == 'Atleta']
            ref = df[df['Tipo'] == 'Referencia']

            # 1. LINHAS DE CONEXÃO (Bem sutis)
            for i, row in at.iterrows():
                cid = int(row['Cluster'])
                r = ref[ref['Cluster'] == cid].iloc[0]
                ax.plot([row['PCA1'], r['PCA1']], [row['PCA2'], r['PCA2']], 
                        c=cores[cid], alpha=0.1, linestyle='-', linewidth=0.5, zorder=1)

            # 2. ATLETAS (Bolinhas)
            for cid in range(5):
                grp = at[at['Cluster'] == cid]
                ax.scatter(grp['PCA1'], grp['PCA2'], 
                           color=cores[cid], s=60, alpha=0.7, edgecolors='white', linewidth=0.5, zorder=2)

            # 3. REFERÊNCIAS (Estrelas) - SEM TEXTO GIGANTE AGORA
            for cid in range(5):
                rf = ref[ref['Cluster'] == cid]
                nm = mapa.get(cid, "Ref")
                
                # Apenas a estrela. O 'label=nm' garante que apareça na legenda.
                ax.scatter(rf['PCA1'], rf['PCA2'], 
                           color=cores[cid], s=500, marker='*', edgecolors='black', linewidth=1.5, zorder=3, label=nm)
                
                # REMOVIDO: ax.text(...) que colocava o nome GIGANTE no meio do gráfico.

            # 4. NOMES DOS ATLETAS (Discretos)
            import random
            for i, row in at.iterrows():
                # Pequeno ajuste aleatório para nomes não ficarem um em cima do outro
                jitter_y = random.uniform(-0.03, 0.03)
                jitter_x = random.uniform(-0.03, 0.03)
                
                ax.text(row['PCA1'] + jitter_x, row['PCA2'] - 0.1 + jitter_y, 
                        row['Nome'], fontsize=6, ha='center', alpha=0.6, zorder=4)

            # Ajustes Finais de Layout
            ax.set_title('Mapa de Clustering (Distribuição dos Atletas)', fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(False) # Sem grades para ficar clean
            
            # Borda do gráfico mais suave
            for spine in ax.spines.values():
                spine.set_edgecolor('#ddd')

            # LEGENDA (Agora ela é a protagonista da identificação)
            # bbox_to_anchor joga a legenda um pouco para fora se precisar, ou mantém no canto
            ax.legend(loc='lower right', title="Perfis (Referências)", fontsize=9, framealpha=0.9, fancybox=True)

            canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
            canvas.draw()
            
            # Barra de ferramentas
            toolbar = NavigationToolbar2Tk(canvas, self.frame_grafico)
            toolbar.update()
            
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e: 
            tk.Label(self.frame_grafico, text=f"Erro: {e}", fg="red").pack()
        
    # -------- Lógica de Seleção --------
    def selecionar_jogador_da_lista(self):
        # 1. Verifica qual item está selecionado na tabela
        item_selecionado = self.tree_lista.selection()
        
        if not item_selecionado:
            messagebox.showwarning("Atenção", "Por favor, clique em um jogador da lista para selecionar.")
            return

        # 2. Pega os valores da linha selecionada
        # (Isso retorna uma lista: [Nome, Data, Peso, ...])
        valores = self.tree_lista.item(item_selecionado, "values")
        
        # 3. Chama a nova tela passando esses dados
        self.abrir_tela_detalhes(valores)

    def abrir_tela_detalhes(self, valores_treeview):
        # 1. Chama o controller
        resultado, msg = self.controller.obter_detalhes_e_predicao(valores_treeview)
        
        if resultado is None:
            messagebox.showerror("Erro", f"Não foi possível ler os dados do atleta.\n{msg}")
            return

        atleta = resultado['atleta']
        posicao = resultado['melhor_posicao']
        dados_graf = resultado['dados_grafico']

        # 2. Configura a tela
        frame = self.frames["detalhes_jogador"]
        
        for widget in frame.winfo_children():
            widget.destroy()

        # --- CABEÇALHO ---
        lbl_titulo = tk.Label(frame, text=f"Seu perfil é de:  [{posicao}]", 
                              bg="#222", fg="white", font=("Arial", 22, "bold"))
        lbl_titulo.pack(side="top", pady=(20, 10))

        # --- RODAPÉ (Botão Retornar) ---
        btn_frame = tk.Frame(frame, bg="#222")
        btn_frame.pack(side="bottom", fill="x", pady=20)
        
        tk.Button(btn_frame, text="Retornar", width=15, height=2, bg="#ddd", font=("Arial", 11),
                  command=lambda: self.mostrar_frame("listar_jogadores")).pack()

        # --- ÁREA DE CONTEÚDO ---
        conteudo = tk.Frame(frame, bg="#222")
        conteudo.pack(side="top", fill="both", expand=True, padx=20, pady=10)

        # >>> LADO ESQUERDO: TEXTO <<<
        frame_texto = tk.Frame(conteudo, bg="#e0e0e0", bd=2, relief="ridge")
        frame_texto.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(frame_texto, text="Dados do atleta:", bg="#d0d0d0", fg="black", font=("Arial", 14)).pack(fill="x", pady=5)

        # --- FUNÇÃO AUXILIAR DE FORMATAÇÃO PARA VIEW ---
        # Garante que, se for número, vira inteiro visualmente.
        def fmt(valor):
            try:
                return int(round(float(valor)))
            except (ValueError, TypeError):
                return valor

        dados_exibir = [
            ("Nome:", atleta["Nome"]),
            ("Data de nascimento:", atleta["Data_formatada"]),
            ("Peso:", f"{fmt(atleta['peso'])} kg"),
            ("Estatura:", f"{fmt(atleta['estatura'])} cm"),
            ("Flexibilidade:", f"{fmt(atleta['flexibilidade'])} cm"),
            ("Abdominal:", f"{fmt(atleta['abdominal'])} rep"),
            ("Arremesso:", f"{fmt(atleta['arremesso'])} m"),
            ("Salto horizontal:", f"{fmt(atleta['Salto horizontal'])} cm"),
            ("Salto Vertical:", f"{fmt(atleta['Salto vertical'])} cm"),
        ]

        for rotulo, valor in dados_exibir:
            f_linha = tk.Frame(frame_texto, bg="#e0e0e0")
            f_linha.pack(fill="x", pady=5, padx=15)
            
            tk.Label(f_linha, text=rotulo, bg="#e0e0e0", fg="black", font=("Arial", 12), anchor="w").pack(side="left")
            tk.Label(f_linha, text=valor, bg="#e0e0e0", fg="black", font=("Arial", 12, "bold"), anchor="e").pack(side="right")

        # >>> LADO DIREITO: GRÁFICO RADAR <<<
        frame_grafico = tk.Frame(conteudo, bg="white", bd=2, relief="ridge")
        frame_grafico.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.desenhar_radar(frame_grafico, dados_graf, posicao)

        self.mostrar_frame("detalhes_jogador")

    def desenhar_radar(self, parent_frame, dados, posicao_nome):
        # Configuração dos dados para o radar fechar o círculo
        labels = dados['labels']
        values = dados['values_atleta']
        
        # O Matplotlib precisa que o primeiro ponto seja repetido no final para fechar a linha
        values += values[:1]
        
        # Calcula os ângulos para cada atributo
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1] # Repete o primeiro ângulo

        # Cria a figura
        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
        
        # Desenha a linha e preenche
        ax.plot(angles, values, color='#1f77b4', linewidth=2)
        ax.fill(angles, values, color='#1f77b4', alpha=0.25)
        
        # Configura os rótulos (Labels)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=9)
        
        # Remove os valores do eixo Y (círculos concêntricos) para ficar mais limpo
        ax.set_yticklabels([])
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0]) # Define grades fixas
        ax.set_ylim(0, 1) # Limite de 0 a 100% (devido à nossa normalização)

        ax.set_title(f"Performance vs Ideal", y=1.08, fontsize=10, color="#555")

        # Coloca no Tkinter
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # Apenas para o Python não reclamar na inicialização, crie o esqueleto inicial
    def tela_detalhes_jogador(self):
        pass

        # --- CRIANDO O GRÁFICO COM MATPLOTLIB ---
        try:
            fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
            
            # Separa atletas e referências
            atletas = df_resultado[df_resultado['Tipo'] == 'Atleta']
            referencias = df_resultado[df_resultado['Tipo'] == 'Referencia']

            # Plota os Atletas (Bolinhas)
            # 'c' define a cor baseada no Cluster, 'cmap' é a paleta de cores
            ax.scatter(atletas['PCA1'], atletas['PCA2'], c=atletas['Cluster'], cmap='viridis', s=100, alpha=0.7, label='Atletas')
            
            # Plota as Referências (Estrelas Vermelhas Grandes)
            ax.scatter(referencias['PCA1'], referencias['PCA2'], c='red', marker='*', s=300, label='Padrão (Ref)')

            # Coloca os nomes nos pontos
            for i, row in df_resultado.iterrows():
                # Se for referência, coloca o nome da posição em negrito
                if row['Tipo'] == 'Referencia':
                    # Ajuste fino na posição do texto (+0.1) para não ficar em cima do ponto
                    ax.text(row['PCA1'], row['PCA2']+0.1, row['Nome'].replace("REF: ", ""), fontsize=9, fontweight='bold', color='darkred')
                else:
                    # Se for atleta, coloca o nome menorzinho
                    ax.text(row['PCA1'], row['PCA2']+0.1, row['Nome'], fontsize=8)

            ax.set_title('Mapa de Perfis (Atletas vs Padrão Polo Aquático)')
            ax.set_xlabel('Dimensão 1 (PCA)')
            ax.set_ylabel('Dimensão 2 (PCA)')
            ax.grid(True, linestyle='--', alpha=0.5)
            ax.legend()

            # Coloca o gráfico no Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            # Caso o matplotlib falhe por algum motivo
            tk.Label(self.frame_grafico, text=f"Erro ao desenhar gráfico: {e}", fg="red").pack()