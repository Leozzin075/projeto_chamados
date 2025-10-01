# ui.py

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
import pandas as pd

import config
import database

# --- LÓGICA DE NAVEGAÇÃO E LOGIN ---
def fazer_login(janela_login, username_entry, password_entry):
    if database.verificar_login(username_entry.get(), password_entry.get()):
        database.registrar_log("LOGIN_SUCCESS", f"Usuário '{database.current_user_name}' logou com sucesso.")
        janela_login.withdraw()
        if database.current_user_profile == "Suporte":
            abrir_painel_suporte(janela_login)
        elif database.current_user_profile == "Usuario":
            abrir_painel_usuario(janela_login)
    else:
        database.registrar_log("LOGIN_FAIL", f"Tentativa de login falhou para o usuário: '{username_entry.get()}'.")
        messagebox.showerror("Erro de Login", "Usuário ou senha inválidos.")

def fazer_logout(janela_atual, janela_login):
    if messagebox.askyesno("Logout", "Tem certeza que deseja sair?"):
        database.registrar_log("LOGOUT", f"Usuário '{database.current_user_name}' desconectou.")
        janela_atual.destroy()
        janela_login.deiconify()

# --- DEFINIÇÕES DAS JANELAS ---
def abrir_janela_login():
    login_root = ttk.Window(themename="cosmo") 
    login_root.title("Login - Sistema de Chamados TI")
    login_root.geometry("400x250"); login_root.resizable(False, False)
    login_root.update_idletasks()
    x = login_root.winfo_screenwidth() // 2 - login_root.winfo_width() // 2
    y = login_root.winfo_screenheight() // 2 - login_root.winfo_height() // 2
    login_root.geometry(f'+{x}+{y}')
    
    frame = ttk.Frame(login_root, padding="30"); frame.pack(fill="both", expand=True)
    
    ttk.Label(frame, text="Username:", font=("-size 10")).pack(fill='x')
    username_entry = ttk.Entry(frame); username_entry.pack(pady=5, fill='x'); username_entry.focus_set()
    
    ttk.Label(frame, text="Password:", font=("-size 10")).pack(pady=(10,0), fill='x')
    password_entry = ttk.Entry(frame, show="*"); password_entry.pack(pady=5, fill='x')
    password_entry.bind("<Return>", lambda e: fazer_login(login_root, username_entry, password_entry))
    
    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=20)
    
    tk.Button(
        button_frame, 
        text="Login", 
        command=lambda: fazer_login(login_root, username_entry, password_entry),
        font=("Segoe UI", 10, "bold"),
        bg="#0d6efd", fg="white", relief="flat", pady=5, padx=20
    ).pack()
    
    login_root.mainloop()

def abrir_janela_detalhes_comum(parent_window, chamado_data, is_suporte, callback_refresh=None):
    detalhes_root = ttk.Toplevel(title="Detalhes do Chamado"); detalhes_root.geometry("600x700"); detalhes_root.transient(parent_window); detalhes_root.grab_set()
    codigo_chamado, _, hotel, solicitante, descricao, status_atual = chamado_data
    main_frame = ttk.Frame(detalhes_root, padding="15"); main_frame.pack(fill="both", expand=True)
    info_frame = ttk.LabelFrame(main_frame, text="Informações Gerais", padding="10", bootstyle="info"); info_frame.pack(fill="x", pady=5)
    ttk.Label(info_frame, text="Código do Chamado:", font=("-weight bold")).grid(row=0, column=0, sticky="w", pady=2)
    ttk.Label(info_frame, text=codigo_chamado).grid(row=0, column=1, sticky="w", pady=2, padx=5)
    ttk.Label(info_frame, text="Hotel:", font=("-weight bold")).grid(row=1, column=0, sticky="w", pady=2); ttk.Label(info_frame, text=hotel).grid(row=1, column=1, sticky="w", pady=2, padx=5)
    ttk.Label(info_frame, text="Solicitante:", font=("-weight bold")).grid(row=2, column=0, sticky="w", pady=2); ttk.Label(info_frame, text=solicitante).grid(row=2, column=1, sticky="w", pady=2, padx=5)
    if not is_suporte:
        ttk.Label(info_frame, text="Status Atual:", font=("-weight bold")).grid(row=3, column=0, sticky="w", pady=2); ttk.Label(info_frame, text=status_atual, bootstyle="primary").grid(row=3, column=1, sticky="w", pady=2, padx=5)
    desc_frame = ttk.LabelFrame(main_frame, text="Descrição Completa", padding="10"); desc_frame.pack(fill="both", pady=5)
    desc_text = ScrolledText(desc_frame, wrap="word", height=6); desc_text.pack(fill="both", expand=True); desc_text.insert(tk.END, descricao); desc_text.configure(state="disabled")
    chat_frame = ttk.LabelFrame(main_frame, text="Histórico / Comentários", padding="10"); chat_frame.pack(fill="both", expand=True, pady=5)
    hist_text = ScrolledText(chat_frame, wrap="word", state="disabled", height=10); hist_text.pack(fill="both", expand=True, pady=(0, 5))
    input_frame = ttk.Frame(chat_frame); input_frame.pack(fill="x")
    comentario_entry = ttk.Entry(input_frame); comentario_entry.pack(side="left", expand=True, fill="x"); comentario_entry.focus_set()
    def _carregar_comentarios():
        hist_text.configure(state="normal"); hist_text.delete("1.0", tk.END)
        comentarios_df = database.buscar_comentarios_por_id(codigo_chamado)
        if not comentarios_df.empty:
            for _, row in comentarios_df.iterrows(): hist_text.insert(tk.END, f"[{row['Timestamp']}] {row['Autor']}:\n{row['Mensagem']}\n\n")
        else: hist_text.insert(tk.END, "Nenhum comentário neste chamado ainda.")
        hist_text.configure(state="disabled"); hist_text.see(tk.END)
    def _enviar_comentario():
        msg = comentario_entry.get().strip()
        if not msg: return
        if database.adicionar_comentario(codigo_chamado, database.current_user_name, msg):
            comentario_entry.delete(0, tk.END); _carregar_comentarios()
        else: messagebox.showerror("Erro", "Não foi possível enviar o comentário.", parent=detalhes_root)
    btn_enviar = ttk.Button(input_frame, text="Enviar", command=_enviar_comentario, bootstyle="info"); btn_enviar.pack(side="right", padx=(5,0)); comentario_entry.bind("<Return>", lambda e: _enviar_comentario())
    if is_suporte:
        acoes_detalhes_frame = ttk.LabelFrame(main_frame, text="Ações de Suporte", padding="10"); acoes_detalhes_frame.pack(fill="x", pady=5)
        ttk.Label(acoes_detalhes_frame, text="Alterar Status:").pack(side="left", padx=5)
        combo_novo_status = ttk.Combobox(acoes_detalhes_frame, values=config.LISTA_STATUS, state="readonly"); combo_novo_status.pack(side="left", padx=5); combo_novo_status.set(status_atual)
        def salvar_novo_status():
            novo_status = combo_novo_status.get()
            if novo_status == status_atual: return
            if database.atualizar_status_por_codigo(codigo_chamado, novo_status, status_atual):
                messagebox.showinfo("Sucesso", "Status atualizado!", parent=detalhes_root)
                if callback_refresh: callback_refresh()
                detalhes_root.destroy()
            else: messagebox.showerror("Erro", "Não foi possível atualizar o status.", parent=detalhes_root)
        ttk.Button(acoes_detalhes_frame, text="Salvar Status", command=salvar_novo_status, bootstyle="success").pack(side="left", padx=10)
    ttk.Button(main_frame, text="Voltar", command=detalhes_root.destroy, bootstyle="secondary").pack(pady=10)
    _carregar_comentarios()

def abrir_painel_usuario(janela_login):
    user_root = ttk.Toplevel(title=f"Portal de Chamados - Bem-vindo, {database.current_user_name}!"); user_root.geometry("900x600")
    user_root.protocol("WM_DELETE_WINDOW", janela_login.destroy)
    main_frame = ttk.Frame(user_root, padding="10"); main_frame.pack(fill="both", expand=True)
    notebook = ttk.Notebook(main_frame); notebook.pack(fill="both", expand=True)
    aba_abrir_chamado, aba_meus_chamados = ttk.Frame(notebook, padding="10"), ttk.Frame(notebook, padding="10")
    notebook.add(aba_abrir_chamado, text="Abrir Novo Chamado"); notebook.add(aba_meus_chamados, text="Meus Chamados")
    form_frame = ttk.LabelFrame(aba_abrir_chamado, text="Informações do Chamado", padding="10", bootstyle="info"); form_frame.pack(fill="x", pady=10)
    ttk.Label(form_frame, text="Hotel:", font=("-weight bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w"); ttk.Label(form_frame, text=database.current_user_hotel).grid(row=0, column=1, padx=5, pady=5, sticky="w")
    ttk.Label(form_frame, text="Descrição do Problema:", font=("-weight bold")).grid(row=1, column=0, padx=5, pady=5, sticky="w")
    text_descricao = ScrolledText(form_frame, height=5, wrap="word"); text_descricao.grid(row=1, column=1, padx=5, pady=5, sticky="ew"); form_frame.columnconfigure(1, weight=1)
    tabela_frame = ttk.Frame(aba_meus_chamados); tabela_frame.pack(fill="both", expand=True, pady=10)
    tree_meus_chamados = ttk.Treeview(tabela_frame, bootstyle="primary"); tree_meus_chamados.pack(fill="both", expand=True)
    def carregar_meus_chamados():
        for i in tree_meus_chamados.get_children(): tree_meus_chamados.delete(i)
        df = pd.DataFrame(database.worksheet_chamados.get_all_records())
        if df.empty: return
        df_meus_chamados = df[df['Solicitante'] == database.current_user_name].sort_values(by="DataHora", ascending=False)
        if not df_meus_chamados.empty:
            tree_meus_chamados["columns"] = ['CodigoChamado', 'DataHora', 'Descricao', 'Status']; tree_meus_chamados["show"] = "headings"
            for col in tree_meus_chamados["columns"]: tree_meus_chamados.heading(col, text=col); tree_meus_chamados.column(col, anchor="w", width=120)
            for _, row in df_meus_chamados.iterrows(): tree_meus_chamados.insert("", "end", values=[row.get(c, '') for c in tree_meus_chamados["columns"]])
    def submeter_novo_chamado():
        descricao = text_descricao.get("1.0", tk.END).strip()
        if not descricao: messagebox.showwarning("Atenção", "Descreva o problema."); return
        novo_codigo = database.gerar_novo_codigo_chamado(); data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S"); nova_linha = [novo_codigo, data_hora, database.current_user_hotel, database.current_user_name, descricao, "Aberto"]
        database.worksheet_chamados.append_row(nova_linha); database.registrar_log("TICKET_CREATED", f"Criou o chamado '{novo_codigo}'.")
        messagebox.showinfo("Sucesso", f"Chamado aberto com sucesso!\nCódigo: {novo_codigo}"); text_descricao.delete("1.0", tk.END); carregar_meus_chamados(); notebook.select(aba_meus_chamados)
    def abrir_detalhes_selecionado_usuario():
        if not tree_meus_chamados.focus(): messagebox.showwarning("Atenção", "Selecione um chamado."); return
        dados_resumidos = tree_meus_chamados.item(tree_meus_chamados.focus(), 'values')
        df_completo = pd.DataFrame(database.worksheet_chamados.get_all_records()); chamado_completo = df_completo[df_completo['CodigoChamado'] == dados_resumidos[0]]
        if not chamado_completo.empty: abrir_janela_detalhes_comum(user_root, chamado_completo.iloc[0].values, is_suporte=False)
    ttk.Button(form_frame, text="Enviar Chamado", command=submeter_novo_chamado, bootstyle="primary").grid(row=2, column=1, sticky="e", padx=5, pady=10)
    botoes_meus_chamados = ttk.Frame(tabela_frame); botoes_meus_chamados.pack(pady=10, fill="x")
    ttk.Button(botoes_meus_chamados, text="Ver Detalhes", command=abrir_detalhes_selecionado_usuario, bootstyle="info").pack(side="left")
    ttk.Button(botoes_meus_chamados, text="Recarregar Lista", command=carregar_meus_chamados, bootstyle="secondary").pack(side="left", padx=10)
    ttk.Button(main_frame, text="Sair (Logout)", command=lambda: fazer_logout(user_root, janela_login), bootstyle="secondary-outline").pack(pady=10, side="bottom")
    carregar_meus_chamados()

def abrir_painel_suporte(janela_login):
    root = ttk.Toplevel(title="Painel de Suporte de TI"); root.geometry("1200x700")
    root.protocol("WM_DELETE_WINDOW", janela_login.destroy)
    main_frame = ttk.Frame(root, padding="10"); main_frame.pack(fill="both", expand=True)
    filtro_frame = ttk.LabelFrame(main_frame, text="Filtros", padding="10"); filtro_frame.pack(fill="x", pady=5)
    ttk.Label(filtro_frame, text="Hotel:").grid(row=0, column=0, padx=5, pady=2)
    combo_filtro_hotel = ttk.Combobox(filtro_frame, values=["Todos"] + config.LISTA_HOTEIS); combo_filtro_hotel.grid(row=0, column=1, padx=5, pady=2); combo_filtro_hotel.set("Todos")
    ttk.Label(filtro_frame, text="Status:").grid(row=0, column=2, padx=5, pady=2)
    combo_filtro_status = ttk.Combobox(filtro_frame, values=["Todos"] + config.LISTA_STATUS); combo_filtro_status.grid(row=0, column=3, padx=5, pady=2); combo_filtro_status.set("Todos")
    ttk.Label(filtro_frame, text="Código/Data:").grid(row=0, column=4, padx=5, pady=2)
    entry_filtro_texto = ttk.Entry(filtro_frame); entry_filtro_texto.grid(row=0, column=5, padx=5, pady=2)
    df_chamados_local = None
    def carregar_dados_chamados():
        nonlocal df_chamados_local
        df_chamados_local = database.buscar_dados_chamados()
        preencher_tabela_chamados(df_chamados_local)
    def aplicar_filtros():
        df_filtrado = df_chamados_local.copy()
        hotel, status, texto = combo_filtro_hotel.get(), combo_filtro_status.get(), entry_filtro_texto.get().strip()
        if hotel and hotel != "Todos": df_filtrado = df_filtrado[df_filtrado['Hotel'] == hotel]
        if status and status != "Todos": df_filtrado = df_filtrado[df_filtrado['Status'] == status]
        if texto: df_filtrado = df_filtrado[df_filtrado['CodigoChamado'].str.contains(texto, case=False) | df_filtrado['DataHora'].str.contains(texto, case=False)]
        preencher_tabela_chamados(df_filtrado)
    def limpar_filtros():
        combo_filtro_hotel.set("Todos"); combo_filtro_status.set("Todos"); entry_filtro_texto.delete(0, tk.END)
        preencher_tabela_chamados(df_chamados_local)
    ttk.Button(filtro_frame, text="Aplicar", command=aplicar_filtros, bootstyle="primary").grid(row=0, column=6, padx=10, pady=2)
    ttk.Button(filtro_frame, text="Limpar", command=limpar_filtros, bootstyle="secondary").grid(row=0, column=7, padx=5, pady=2)
    tabela_frame = ttk.LabelFrame(main_frame, text="Chamados", padding="10"); tabela_frame.pack(fill="both", expand=True, pady=10)
    tree_chamados = ttk.Treeview(tabela_frame, bootstyle="primary"); tree_chamados.pack(fill="both", expand=True)
    scrollbar = ttk.Scrollbar(tabela_frame, orient="vertical", command=tree_chamados.yview); scrollbar.pack(side="right", fill="y"); tree_chamados.configure(yscrollcommand=scrollbar.set)
    acoes_frame = ttk.LabelFrame(main_frame, text="Ações", padding="10"); acoes_frame.pack(fill="x", expand=False)
    def preencher_tabela_chamados(df):
        for i in tree_chamados.get_children(): tree_chamados.delete(i)
        if df is not None and not df.empty:
            tree_chamados["columns"] = list(df.columns); tree_chamados["show"] = "headings"
            for column in tree_chamados["columns"]: tree_chamados.heading(column, text=column); tree_chamados.column(column, width=120)
            for _, row in df.iterrows(): tree_chamados.insert("", "end", values=list(row))
    def abrir_detalhes_selecionado_suporte():
        if not tree_chamados.focus(): messagebox.showwarning("Atenção", "Selecione um chamado."); return
        abrir_janela_detalhes_comum(root, tree_chamados.item(tree_chamados.focus(), 'values'), is_suporte=True, callback_refresh=carregar_dados_chamados)
    ttk.Button(acoes_frame, text="Ver Detalhes", command=abrir_detalhes_selecionado_suporte, bootstyle="info").pack(side="left", padx=5)
    ttk.Button(acoes_frame, text="Recarregar Lista", command=carregar_dados_chamados, bootstyle="secondary").pack(side="left", padx=5)
    ttk.Button(acoes_frame, text="Gerenciar Usuários", command=lambda: abrir_janela_usuarios(root)).pack(side="right", padx=5)
    ttk.Button(acoes_frame, text="Sair (Logout)", command=lambda: fazer_logout(root, janela_login), bootstyle="secondary-outline").pack(side="right", padx=5)
    carregar_dados_chamados()

def abrir_janela_usuarios(parent_window):
    janela_usuarios = ttk.Toplevel(title="Gerenciamento de Usuários"); janela_usuarios.geometry("700x500"); janela_usuarios.transient(parent_window); janela_usuarios.grab_set()
    main_frame = ttk.Frame(janela_usuarios, padding="10"); main_frame.pack(fill="both", expand=True)
    tabela_frame = ttk.LabelFrame(main_frame, text="Usuários Cadastrados", padding="5"); tabela_frame.pack(fill="both", expand=True, pady=5)
    tree_usuarios = ttk.Treeview(tabela_frame, bootstyle="info"); tree_usuarios.pack(fill="both", expand=True)
    form_frame = ttk.LabelFrame(main_frame, text="Dados do Usuário", padding="10"); form_frame.pack(fill="x", pady=5)
    ttk.Label(form_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="w"); entry_user = ttk.Entry(form_frame); entry_user.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    ttk.Label(form_frame, text="Password:").grid(row=0, column=2, padx=5, pady=5, sticky="w"); entry_pass = ttk.Entry(form_frame); entry_pass.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
    ttk.Label(form_frame, text="Hotel:").grid(row=1, column=0, padx=5, pady=5, sticky="w"); combo_hotel = ttk.Combobox(form_frame, values=config.LISTA_HOTEIS_PARA_CADASTRO); combo_hotel.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    ttk.Label(form_frame, text="Profile:").grid(row=1, column=2, padx=5, pady=5, sticky="w"); combo_profile = ttk.Combobox(form_frame, values=["Usuario", "Suporte"], state="readonly"); combo_profile.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
    form_frame.columnconfigure(1, weight=1); form_frame.columnconfigure(3, weight=1)
    def _carregar():
        for i in tree_usuarios.get_children(): tree_usuarios.delete(i)
        df = database.buscar_todos_usuarios()
        if not df.empty:
            tree_usuarios["columns"] = list(df.columns); tree_usuarios["show"] = "headings"
            for col in df.columns: tree_usuarios.heading(col, text=col)
            for _, row in df.iterrows(): tree_usuarios.insert("", "end", values=list(row))
    def _on_select(event):
        entry_user.delete(0, tk.END); entry_pass.delete(0, tk.END); combo_hotel.set(''); combo_profile.set('')
        if tree_usuarios.focus():
            u, p, h, pr = tree_usuarios.item(tree_usuarios.focus())['values']
            entry_user.insert(0, u); entry_pass.insert(0, p); combo_hotel.set(h); combo_profile.set(pr)
    tree_usuarios.bind('<<TreeviewSelect>>', _on_select)
    def _salvar():
        u, p, h, pr = entry_user.get().strip(), entry_pass.get().strip(), combo_hotel.get().strip(), combo_profile.get().strip()
        if not all([u, p, h, pr]): messagebox.showwarning("Atenção", "Todos os campos são obrigatórios!"); return
        is_edit = bool(tree_usuarios.selection())
        if database.salvar_usuario(u, p, h, pr, is_edit):
            messagebox.showinfo("Sucesso", f"Usuário {'editado' if is_edit else 'salvo'} com sucesso!")
            _limpar(); _carregar()
    def _limpar():
        entry_user.delete(0, tk.END); entry_pass.delete(0, tk.END); combo_hotel.set(''); combo_profile.set('')
        if tree_usuarios.selection(): tree_usuarios.selection_remove(tree_usuarios.selection()); entry_user.focus_set()
    def _deletar():
        if not tree_usuarios.focus(): messagebox.showwarning("Atenção", "Selecione um usuário."); return
        username_a_deletar = tree_usuarios.item(tree_usuarios.focus(), 'values')[0]
        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja deletar o usuário {username_a_deletar}?"):
            if database.deletar_usuario(username_a_deletar):
                messagebox.showinfo("Sucesso", "Usuário deletado!")
                _limpar(); _carregar()
    botoes_frame = ttk.Frame(janela_usuarios); botoes_frame.pack(fill="x", pady=10, padx=10)
    ttk.Button(botoes_frame, text="Salvar (Novo/Editar)", command=_salvar, bootstyle="success").pack(side="left", expand=True, fill="x", padx=5)
    ttk.Button(botoes_frame, text="Limpar Campos", command=_limpar, bootstyle="secondary").pack(side="left", expand=True, fill="x", padx=5)
    ttk.Button(botoes_frame, text="Deletar Usuário", command=_deletar, bootstyle="danger").pack(side="left", expand=True, fill="x", padx=5)
    _carregar()

if __name__ == "__main__":
    if conectar_google_sheets():
        abrir_janela_login()