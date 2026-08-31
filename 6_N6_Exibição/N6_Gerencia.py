# Exibição | Gerência [RSSI, SNR e PSR] | N6 | WissTek-IoT | Framework LoRa
# 31/08/2026
#====== Nível 6 - Gerência ======
# Gráficos de RSSI e PSR
import tkinter as tk
from tkinter import messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.style as style

style.use("ggplot")

MAX_PONTOS = 600
cor_rssi_down = "#1f77b4"
cor_rssi_up = "#ff7f0e"
cor_snr_down = "#1f77b4"
cor_snr_up = "#ff7f0e"
cor_psr = "#2ca02c"

# ===================== ATUALIZA GRÁFICOS =====================
def atualizar_grafico(ax1, ax2, ax3, canvas1, canvas2, canvas3, raiz, label_down, label_up, label_snr_down, label_snr_up, label_psr):
    rssi_down = []
    rssi_up = []
    snr_down = []
    snr_up = []   
    psr = []

    # ===================== RSSI =====================
    try:
        with open("../4_N4_Armazenamento/Dados_Processados/rssi.tmp", 'r') as f:
            for linha in f:
                linha = linha.strip()
                if linha:
                    try:
                        partes = linha.split()
                        down = float(partes[0].replace(",", "."))
                        up = float(partes[1].replace(",", "."))
                        snr_dl_down = float(partes[2].replace(",", "."))
                        snr_ul_up = float(partes[3].replace(",", "."))                        
                        rssi_down.append(down)
                        rssi_up.append(up)
                        snr_down.append(snr_dl_down)
                        snr_up.append(snr_ul_up)                        
                    except:
                        pass
    except FileNotFoundError:
        pass

    # ===================== PSR =====================
    try:
        with open("../4_N4_Armazenamento/Dados_Processados/psr.tmp", 'r') as f:
            for linha in f:
                linha = linha.strip()
                if linha:
                    try:
                        psr.append(float(linha))
                    except ValueError:
                        pass
    except FileNotFoundError:
        pass

    # ===================== JANELA DESLIZANTE =====================
    rssi_down = rssi_down[-MAX_PONTOS:]
    rssi_up = rssi_up[-MAX_PONTOS:]
    snr_down = snr_down[-MAX_PONTOS:]
    snr_up = snr_up[-MAX_PONTOS:]    
    psr = psr[-MAX_PONTOS:]

    # ===================== LABELS =====================
    if rssi_down:
        label_down.config(text="RSSI DL atual: " + str(round(rssi_down[-1],2)) + " dBm")
    else:
        label_down.config(text="RSSI DL atual: --")

    if rssi_up:
        label_up.config(text="RSSI UL atual: " + str(round(rssi_up[-1],2)) + " dBm")
    else:
        label_up.config(text="RSSI UL atual: --")

    if snr_down:
        label_snr_down.config(text="SNR DL atual: " + str(round(snr_down[-1],2)) + " dB")
    else:
        label_snr_down.config(text="SNR DL atual: --")

    if snr_up:
        label_snr_up.config(text="SNR UL atual: " + str(round(snr_up[-1],2)) + " dB")
    else:
        label_snr_up.config(text="SNR UL atual: --")

    if psr:
        label_psr.config(text="PSR atual: " + str(round(psr[-1],2)) + " %")
    else:
        label_psr.config(text="PSR atual: --")

    # ===================== GRÁFICO RSSI =====================
    ax1.clear()
    if rssi_down:
        ax1.plot(
            rssi_down,
            label="RSSI Downlink (dBm)",
            linewidth=1.5,
            marker='o',
            markersize=3,
            color=cor_rssi_down
        )
    if rssi_up:
        ax1.plot(
            rssi_up,
            label="RSSI Uplink (dBm)",
            linewidth=1.5,
            marker='s',
            markersize=3,
            color=cor_rssi_up
        )
    if rssi_down or rssi_up:
        ax1.legend(loc='upper right')
        todos_rssi = rssi_down + rssi_up
        val_min = min(todos_rssi)
        val_max = max(todos_rssi)
        margem = (val_max - val_min) * 0.10
        if margem == 0:
            margem = 5
        ax1.set_ylim(val_min - margem, val_max + margem)

    ax1.legend(fontsize=8)
    ax1.set_title("RSSI LoRa (Downlink / Uplink)", fontsize=10)
    ax1.set_ylabel("RSSI (dBm)")
    ax1.set_xlabel("Últimas " + str(MAX_PONTOS) + " medidas")

    # ===================== GRÁFICO SNR =====================
    ax2.clear()
    if snr_down:
        ax2.plot(
            snr_down,
            label="SNR Downlink (dBm)",
            linewidth=1.5,
            marker='o',
            markersize=3,
            color=cor_snr_down
        )
    if snr_up:
        ax2.plot(
            snr_up,
            label="SNR Uplink (dBm)",
            linewidth=1.5,
            marker='s',
            markersize=3,
            color=cor_snr_up
        )
    if snr_down or snr_up:
        ax2.legend(loc='upper right')
        todos_snr = snr_down + snr_up
        val_snr_min = min(todos_snr)
        val_snr_max = max(todos_snr)
        margem_snr = (val_snr_max - val_snr_min) * 0.10
        if margem == 0:
            margem = 5
        ax2.set_ylim(val_snr_min - margem_snr, val_snr_max + margem_snr)

    ax2.legend(fontsize=8)
    ax2.set_title("SNR LoRa (Downlink / Uplink)", fontsize=10)
    ax2.set_ylabel("SNR (dB)")
    ax2.set_xlabel("Últimas " + str(MAX_PONTOS) + " medidas")

    # ===================== GRÁFICO PSR =====================
    ax3.clear()
    if psr:
        ax3.plot(
            psr,
            label="PSR (%)",
            linewidth=1.5,
            marker='o',
            markersize=3,
            color=cor_psr
        )
        ax3.legend(loc='upper right')
        val_min = min(psr)
        val_max = max(psr)
        margem = (val_max - val_min) * 0.10
        if margem == 0:
            margem = 5
        ax3.set_ylim(max(0, val_min - margem), min(105, val_max + margem))

    ax3.legend(fontsize=8)
    ax3.set_title("Packet Success Rate - PSR", fontsize=10)
    ax3.set_ylabel("PSR (%)")
    ax3.set_xlabel("Últimas " + str(MAX_PONTOS) + " medidas")

    # ===================== ATUALIZA =====================
    canvas1.draw()
    canvas2.draw()
    canvas3.draw()
    raiz.after(1000,atualizar_grafico,ax1,ax2,ax3,canvas1,canvas2,canvas3,raiz,label_down,label_up,label_snr_down,label_snr_up,label_psr)

# ===================== BOTÕES =====================
def fechar():
    if messagebox.askokcancel("Sair","Deseja fechar o monitor?"):
        raiz.destroy()

def salvar(fig1, fig2, fig3):
    arquivo = filedialog.asksaveasfilename(defaultextension=".png")
    if arquivo:
        fig1.savefig(arquivo.replace(".png","_rssi.png"))
        fig2.savefig(arquivo.replace(".png","_snr.png"))
        fig3.savefig(arquivo.replace(".png","_psr.png"))

# ===================== INTERFACE =====================
raiz = tk.Tk()
raiz.title("FEE247 - NÍVEL 6 - GERÊNCIA")
raiz.geometry("1000x980")

# ===================== LABELS DAS RSSIS =====================
frame_labels_rssi = tk.Frame(raiz)
frame_labels_rssi.pack(fill="x", padx=10, pady=(10,5))

label_down = tk.Label(frame_labels_rssi,text="RSSI DL atual: --",font=("Arial",10,"bold"),bg=cor_rssi_down,fg="white",relief="ridge",bd=3,width=20,pady=4)
label_down.pack(side="left",padx=5)

label_up = tk.Label(frame_labels_rssi,text="RSSI UL atual: --",font=("Arial",10,"bold"),bg=cor_rssi_up,fg="white",relief="ridge",bd=3,width=20,pady=4)
label_up.pack(side="left",padx=5)


# ===================== BOTAO SALVAR =====================

btn = tk.Button(frame_labels_rssi,text="Salvar Gráficos",command=lambda: salvar(fig1,fig2,fig3))
btn.pack(side="right",pady=5)


# ===================== GRÁFICO DAS RSSIS =====================
frame_rssi = tk.Frame(raiz)
frame_rssi.pack(fill="both", expand=True, padx=10, pady=5)

fig1 = Figure(figsize=(10, 1.8))
ax1 = fig1.add_subplot(111)
canvas1 = FigureCanvasTkAgg(fig1,master=frame_rssi)
canvas1.get_tk_widget().pack(fill="both",expand=True)


# ===================== LABELS DAS SNRS =====================
frame_labels_snr = tk.Frame(raiz)
frame_labels_snr.pack(fill="x", padx=10, pady=(10,5))

label_snr_down = tk.Label(frame_labels_snr,text="SNR DL atual: --",font=("Arial",10,"bold"),bg=cor_snr_down,fg="white",relief="ridge",bd=3,width=20,pady=4)
label_snr_down.pack(side="left",padx=5)

label_snr_up = tk.Label(frame_labels_snr,text="SNR UL atual: --",font=("Arial",10,"bold"),bg=cor_snr_up,fg="white",relief="ridge",bd=3,width=20,pady=4)
label_snr_up.pack(side="left",padx=5)

# ===================== GRÁFICO DAS SNRS =====================
frame_snr = tk.Frame(raiz)
frame_snr.pack(fill="both", expand=True, padx=10, pady=5)

fig2 = Figure(figsize=(10, 1.8))
ax2 = fig2.add_subplot(111)
canvas2 = FigureCanvasTkAgg(fig2,master=frame_snr)
canvas2.get_tk_widget().pack(fill="both",expand=True)


# ===================== LABEL DA PSR =====================
frame_label_psr = tk.Frame(raiz)
frame_label_psr.pack(fill="x", padx=10, pady=5)

label_psr = tk.Label(frame_label_psr,text="PSR atual: --",font=("Arial",10,"bold"),bg=cor_psr,fg="white",relief="ridge",bd=3,width=15,pady=4)
label_psr.pack(side="left",padx=5)

# ===================== GRÁFICO DA PSR =====================
frame_psr = tk.Frame(raiz)
frame_psr.pack(fill="both", expand=True, padx=10, pady=5)

fig3 = Figure(figsize=(10, 1.8))
ax3 = fig3.add_subplot(111)
canvas3 = FigureCanvasTkAgg(fig3,master=frame_psr)
canvas3.get_tk_widget().pack(fill="both",expand=True)

atualizar_grafico(ax1,ax2,ax3,canvas1,canvas2,canvas3,raiz,label_down,label_up,label_snr_down,label_snr_up,label_psr)
raiz.protocol("WM_DELETE_WINDOW",fechar)

raiz.mainloop()
