import tkinter as tk
from tkinter import ttk, messagebox
import csv # <--- MUDANÇA: Usaremos a biblioteca CSV
import os
from datetime import datetime

# --- CONFIGURAÇÃO ---
CAMINHO_ONEDRIVE = r"C:\Users\Tecnologia\OneDrive\Desktop\CHAMADOS_HOTEIS"
# MUDANÇA: O novo arquivo será um .csv
NOME_ARQUIVO_LOG = "novos_chamados.csv" 
CAMINHO_COMPLETO_ARQUIVO = os.path.join(CAMINHO_ONEDRIVE, NOME_ARQUIVO_LOG)

LISTA_HOTEIS = ["Hotel Acalanto", "Hotel Classe", "Hotel Unico", "Hotel Atmosfera"]
# --- FIM DA CONFIGURAÇÃO ---


def verificar_e_criar_cabecalho():
    """Verifica se o arquivo CSV existe e, se não, cria com o cabeçalho."""
    if not os.path.exists(CAMINHO_COMPLETO_ARQUIVO):
        with open(CAMINHO_COMPLETO_ARQUIVO, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';') # Usando ';' como delimitador
            writer.writerow(['DataHora', 'Hotel', 'Solicitante', 'Descricao', 'Status'])

def salvar_chamado():
    nome = entry_nome.get()
    hotel = combo_hotel.get()
    descricao = text_descricao.get("1.0", tk.END).strip()

    if not nome or not hotel or not descricao:
        messagebox.showwarning("Atenção", "Todos os campos são obrigatórios!")
        return
    
    data_hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    novo_chamado = [data_hora_atual, hotel, nome, descricao, "Aberto"]

    try:
        # <--- MUDANÇA RADICAL AQUI ---
        # A lógica agora é muito mais simples: apenas adiciona uma nova linha no final do arquivo.
        # 'a' significa 'append' (adicionar).
        with open(CAMINHO_COMPLETO_ARQUIVO, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';') # Usando ';' para evitar problemas com vírgulas na descrição
            writer.writerow(novo_chamado)
        
        messagebox.showinfo("Sucesso", "Chamado registrado com sucesso!")
        limpar_campos()
        
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao salvar o chamado.\n\nDetalhes: {e}")

def limpar_campos():
    entry_nome.delete(0, tk.END)
    combo_hotel.set('')
    text_descricao.delete("1.0", tk.END)
    entry_nome.focus_set()

# --- INTERFACE GRÁFICA (Permanece a mesma) ---
# ... (O código da interface a partir daqui é idêntico ao anterior, não precisa mudar)
root = tk.Tk()
root.title("Sistema de Abertura de Chamados de TI")
root.geometry("550x400")
root.minsize(450, 380)

style = ttk.Style(root)
if "vista" in style.theme_names():
    style.theme_use("vista") 
else:
    style.theme_use("clam")

main_frame = ttk.Frame(root, padding="10 10 10 10")
main_frame.pack(fill="both", expand=True)
main_frame.columnconfigure(0, weight=1)

label_titulo = ttk.Label(main_frame, text="Registro de Novo Chamado", font=("Segoe UI", 16, "bold"))
label_titulo.grid(row=0, column=0, pady=(0, 20), sticky="ew")

labelframe_chamado = ttk.LabelFrame(main_frame, text="Informações do Chamado", padding="10")
labelframe_chamado.grid(row=1, column=0, sticky="ew")
labelframe_chamado.columnconfigure(0, weight=1)

label_nome = ttk.Label(labelframe_chamado, text="Seu Nome:")
label_nome.grid(row=0, column=0, sticky="w", pady=(0, 2))
entry_nome = ttk.Entry(labelframe_chamado)
entry_nome.grid(row=1, column=0, sticky="ew", pady=(0, 10))

label_hotel = ttk.Label(labelframe_chamado, text="Selecione o Hotel:")
label_hotel.grid(row=2, column=0, sticky="w", pady=(0, 2))
combo_hotel = ttk.Combobox(labelframe_chamado, values=LISTA_HOTEIS, state="readonly")
combo_hotel.grid(row=3, column=0, sticky="ew", pady=(0, 10))

label_descricao = ttk.Label(labelframe_chamado, text="Descrição do Problema:")
label_descricao.grid(row=4, column=0, sticky="w", pady=(0, 2))
text_descricao = tk.Text(labelframe_chamado, height=6)
text_descricao.grid(row=5, column=0, sticky="ew", pady=(0, 10))

button_enviar = ttk.Button(main_frame, text="Enviar Chamado", command=salvar_chamado, style="Accent.TButton")
button_enviar.grid(row=2, column=0, sticky="ew", pady=15)

style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

# Verifica/cria o arquivo CSV antes de iniciar o app
verificar_e_criar_cabecalho() 
entry_nome.focus_set()
root.mainloop()