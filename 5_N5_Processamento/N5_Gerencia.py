# Abstração | Gerência [RSSI, SNR e PSR] | N5 | WissTek-IoT | Framework LoRa
# 31/08/2026
#====== Nível 5 - Gerência ======
# Extrai RSSI dos dados brutos e calcula a PSR
import time
import os

# Pasta do Nível 4 (4_N4_Armazenamento)
PASTA_N4 = "../4_N4_Armazenamento"

# Arquivos utilizados pelo nível 5 de gerência
arquivo_rssi = f"{PASTA_N4}/Dados_Processados/rssi.tmp"
arquivo_psr = f"{PASTA_N4}/Dados_Processados/psr.tmp"

# Garante que a pasta de Dados_Processados existe
if not os.path.exists(f"{PASTA_N4}/Dados_Processados"):
    os.mkdir(f"{PASTA_N4}/Dados_Processados")

while True:

    # Procura o último arquivo de dados brutos gravado no nível 4
    arquivo_entrada = ""
    arquivos = os.listdir(f"{PASTA_N4}/Dados_Brutos")
    arquivos.sort()
    for nome in arquivos:
        if nome.endswith(".txt"):
            arquivo_entrada = f"{PASTA_N4}/Dados_Brutos/" + nome

    # Abre o arquivo de dados brutos
    arquivo = open(arquivo_entrada,"r")
    linhas = arquivo.readlines()
    arquivo.close()

    # Listas que guardam os valores calculados
    rssi_down = []
    rssi_up = []
    snr_down = []
    snr_up = []
    psr = []

    # Contadores usados para calcular a PSR
    total_pacotes = 0
    pacotes_recebidos = 0

    # Começa em 1 para pular o cabeçalho do arquivo
    for i in range(1,len(linhas)):
        partes = linhas[i].split(",")
        total_pacotes = total_pacotes + 1

        # Se todos os bytes do UL forem diferente de 9, considera pacote recebido
        pacote_recebido = 0
        for j in range(20):
            if int(partes[22+j]) != 9:
                pacote_recebido = 1

        if pacote_recebido == 1:
            pacotes_recebidos = pacotes_recebidos + 1

            # RSSI de downlink no byte UL_B0 (Posição 38)
            UL_B0 = int(partes[22]) #22 aaf
            if UL_B0 > 128:
                RSSI_DL = ((UL_B0-256)/2.0)-74
            else:
                RSSI_DL = (UL_B0/2.0)-74

            # SNR de downlink no byte UL_B1 (Posição 39)
            UL_B1 = int(partes[23])
            SNR_DL = round(((UL_B1 / 4) - 30),2)

            # RSSI de uplink no byte UL_B2 (Posição 40)
            UL_B2 = int(partes[24])
            if UL_B2 > 128:
                RSSI_UL = ((UL_B2-256)/2.0)-74
            else:
                RSSI_UL = (UL_B2/2.0)-74

            # SNR de downlink no byte UL_B3 (Posição 41)
            UL_B3 = int(partes[25])
            SNR_UL = round(((UL_B3 / 4) - 30),2)

            rssi_down.append(RSSI_DL)
            rssi_up.append(RSSI_UL)
            snr_down.append(SNR_DL)
            snr_up.append(SNR_UL)


        # Calcula a PSR acumulada até este pacote
        PSR = (pacotes_recebidos/total_pacotes)*100
        psr.append(PSR)

    # Grava as RSSIs em arquivo temporário
    f_rssi = open(arquivo_rssi,"w")
    for i in range(len(rssi_down)):
        print(rssi_down[i],rssi_up[i],snr_down[i],snr_up[i],file=f_rssi)
    f_rssi.close()

    # Grava a PSR em arquivo temporário
    f_psr = open(arquivo_psr,"w")
    for i in range(len(psr)):
        print(psr[i],file=f_psr)
    f_psr.close()

    print("Arquivo = ",arquivo_entrada," | Pacotes = ",total_pacotes," | Recebidos = ",pacotes_recebidos," | PSR = ",PSR, "| RSSI Downlink = ", RSSI_DL, "| RSSI Uplink = ", RSSI_UL, "| SNR Downlink = ", SNR_DL, "| SNR Uplink = ", SNR_UL)
    time.sleep(1)
