# database.py

import gspread
import pandas as pd
from datetime import datetime
from tkinter import messagebox
import config
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

worksheet_chamados, worksheet_usuarios, worksheet_comentarios, worksheet_logs = None, None, None, None
df_usuarios = None
current_user_profile, current_user_name, current_user_hotel = None, None, None

def conectar_google_sheets():
    global worksheet_chamados, worksheet_usuarios, worksheet_comentarios, worksheet_logs, df_usuarios
    try:
        caminho_credencial = resource_path(config.ARQUIVO_CREDENCIAL)
        gc = gspread.service_account(filename=caminho_credencial)
        sh = gc.open(config.NOME_PLANILHA)
        worksheet_chamados = sh.worksheet("Chamados")
        worksheet_usuarios = sh.worksheet("Usuarios")
        worksheet_comentarios = sh.worksheet("Comentarios")
        worksheet_logs = sh.worksheet("Logs")
        df_usuarios = pd.DataFrame(worksheet_usuarios.get_all_records())
        return True
    except gspread.exceptions.WorksheetNotFound as e:
        messagebox.showerror("Erro de Planilha", f"Aba não encontrada: {e}\nGaranta que as abas 'Chamados', 'Usuarios', 'Comentarios' e 'Logs' existem.")
        return False
    except Exception as e:
        messagebox.showerror("Erro Crítico de Conexão", f"Não foi possível conectar à base de dados.\nDetalhes: {e}")
        return False

def registrar_log(action, details):
    try:
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        username = current_user_name if current_user_name else "Sistema"
        worksheet_logs.append_row([timestamp, username, action, details])
    except Exception as e:
        print(f"ERRO AO REGISTRAR LOG: {e}")

def gerar_novo_codigo_chamado():
    hoje_str = datetime.now().strftime("%Y-%m-%d")
    todos_codigos = worksheet_chamados.col_values(1)[1:]
    codigos_de_hoje = [c for c in todos_codigos if c.startswith(hoje_str)]
    proximo_sequencial = len(codigos_de_hoje) + 1
    return f"{hoje_str}-{proximo_sequencial:03d}"

def verificar_login(username, password):
    global current_user_profile, current_user_name, current_user_hotel
    if df_usuarios is None: return False
    input_user, input_pass = username.strip(), password.strip()
    usuarios_db = df_usuarios.copy()
    if 'Username' not in usuarios_db.columns or 'Password' not in usuarios_db.columns:
        messagebox.showerror("Erro de Configuração", "A planilha 'Usuarios' não contém as colunas 'Username' e 'Password'.")
        return False
    usuarios_db['Username'] = usuarios_db['Username'].astype(str).str.strip()
    usuarios_db['Password'] = usuarios_db['Password'].astype(str).str.strip()
    usuario_encontrado = usuarios_db[(usuarios_db['Username'].str.lower() == input_user.lower()) & (usuarios_db['Password'] == input_pass)]
    if not usuario_encontrado.empty:
        current_user_profile = usuario_encontrado['Profile'].iloc[0]
        current_user_name = usuario_encontrado['Username'].iloc[0]
        current_user_hotel = usuario_encontrado['Hotel'].iloc[0]
        return True
    return False

def buscar_comentarios_por_id(chamado_id):
    try:
        todos_comentarios = pd.DataFrame(worksheet_comentarios.get_all_records())
        if todos_comentarios.empty: return pd.DataFrame()
        todos_comentarios['ID_Chamado'] = todos_comentarios['ID_Chamado'].astype(str)
        chamado_id = str(chamado_id)
        return todos_comentarios[todos_comentarios['ID_Chamado'] == chamado_id].sort_values(by='Timestamp')
    except Exception as e:
        print(f"Erro ao buscar comentários: {e}"); return pd.DataFrame()

def adicionar_comentario(chamado_id, autor, mensagem):
    try:
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        nova_linha = [str(chamado_id), timestamp, autor, mensagem]
        worksheet_comentarios.append_row(nova_linha)
        registrar_log("ADD_COMMENT", f"Adicionou comentário ao chamado '{chamado_id}'.")
        return True
    except Exception as e:
        print(f"Erro ao adicionar comentário: {e}"); return False

def buscar_dados_chamados():
    if worksheet_chamados:
        df = pd.DataFrame(worksheet_chamados.get_all_records())
        if not df.empty:
            colunas = ['CodigoChamado', 'DataHora', 'Hotel', 'Solicitante', 'Descricao', 'Status']
            for col in colunas:
                if col not in df.columns: df[col] = ''
            return df[colunas]
    return pd.DataFrame()

def atualizar_status_por_codigo(codigo_chamado, novo_status, status_antigo):
    try:
        cell = worksheet_chamados.find(codigo_chamado, in_column=1)
        worksheet_chamados.update_cell(cell.row, 6, novo_status)
        registrar_log("STATUS_CHANGE", f"Status do chamado '{codigo_chamado}' alterado de '{status_antigo}' para '{novo_status}'.")
        return True
    except Exception as e:
        print(f"Erro ao atualizar status: {e}"); return False

def buscar_todos_usuarios():
    df_usuarios_recarregado = pd.DataFrame(worksheet_usuarios.get_all_records())
    return df_usuarios_recarregado

def salvar_usuario(username, password, hotel, profile, is_edit_mode):
    try:
        if is_edit_mode:
            cell = worksheet_usuarios.find(username, in_column=1)
            worksheet_usuarios.update(f'A{cell.row}:D{cell.row}', [[username, password, hotel, profile]])
            registrar_log("USER_EDIT", f"Editou o usuário '{username}'.")
        else:
            todos_usuarios = worksheet_usuarios.get_all_records()
            usernames_existentes = [user['Username'].lower().strip() for user in todos_usuarios]
            if username.lower().strip() in usernames_existentes:
                messagebox.showwarning("Atenção", f"O nome de usuário '{username}' já existe.")
                return False
            else:
                worksheet_usuarios.append_row([username, password, hotel, profile])
                registrar_log("USER_CREATE", f"Criou o novo usuário '{username}'.")
        return True
    except Exception as e:
        messagebox.showerror("Erro de Banco de Dados", f"Ocorreu um erro ao salvar o usuário.\n\nDetalhe Técnico: {e}")
        return False

def deletar_usuario(username):
    try:
        cell = worksheet_usuarios.find(username, in_column=1)
        worksheet_usuarios.delete_rows(cell.row)
        registrar_log("USER_DELETE", f"Deletou o usuário '{username}'.")
        return True
    except Exception as e:
        messagebox.showerror("Erro ao Deletar", f"Não foi possível deletar o usuário.\n\nDetalhe Técnico: {e}")
        return False