# Exibição | Controle LED | N6 | WissTek-IoT | Framework LoRa
# 31/08/2026
#========== Nível 6 =============
# Comando do LED amarelo
import tkinter as tk
import os
# Define o caminho do arquivo dentro do diretório 4_N4_Armazenamento
PASTA_N4 = "../4_N4_Armazenamento"
if not os.path.exists(PASTA_N4):
    os.mkdir(PASTA_N4)
if not os.path.exists(f"{PASTA_N4}/Parametros"):
    os.mkdir(f"{PASTA_N4}/Parametros")
caminho_arquivo = f"{PASTA_N4}/Parametros/cmd_led_amarelo.txt"
# Função para salvar o valor
def salvar_valor(valor):
    with open(caminho_arquivo, "w") as f:
        f.write(str(valor))
    print(f"Valor {valor} salvo em: {caminho_arquivo}")
# Criando a janela
janela = tk.Tk()
janela.title("Controle LED Amarelo")
janela.geometry("300x150")
# Variável da opção
opcao = tk.IntVar(value=0)
# Interface
tk.Label(janela, text="Selecione 0 ou 1:", font=("Arial", 12)).pack(pady=10)
tk.Radiobutton(janela, text="0", variable=opcao, value=0).pack()
tk.Radiobutton(janela, text="1", variable=opcao, value=1).pack()
tk.Button(janela, text="Salvar",
          command=lambda: salvar_valor(opcao.get())).pack(pady=10)
# Executa
janela.mainloop()
