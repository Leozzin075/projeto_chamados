# main.py

import database
import ui
from tkinter import messagebox

if __name__ == "__main__":
    if database.conectar_google_sheets():
        ui.abrir_janela_login()
    else:
        # A mensagem de erro já é exibida pela função de conexão.
        print("Falha na conexão com a base de dados. Encerrando o programa.")