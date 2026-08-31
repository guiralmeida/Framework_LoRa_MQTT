# MoT LoRa MQTT + Borda | N2 e N3 | WissTek-IoT | Framework LoRa MQTT
# 31/08/2026
# ========================== 1 - Bibliotecas
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import math
import time
import struct
from time import localtime, strftime
import os
import threading

# ===== Configurações MQTT =====
BROKER        = "broker.hivemq.com"
#BROKER        = "test.mosquitto.org"
PORTA_MQTT    = 1883

# MODIFIQUE O TOPIC_DL E TOPIC_UL de acordo com SEU_NOME
TOPIC_DL      = "mot_lora_mqtt_SEU_NOME/gateway/downlink"   # Python publica → ESP32 assina
TOPIC_UL      = "mot_lora_mqtt_SEU_NOME/gateway/uplink"     # ESP32 publica  → Python assina

# QoS usado nos dois sentidos (DL e UL). QoS1 = "at least once": o broker
# confirma (PUBACK) e há retransmissão se a confirmação não chegar.
# Importante para o dado de luminosidade, que é a peça central do framework.
MQTT_QOS      = 1
estado_mqtt   = 0

#Tamanho_pacote = input("Tamanho do pacote em bytes = ")
Tamanho_pacote = 20

# Evento para sinalizar chegada de pacote UL
Pacote_UL_status  = threading.Event()
Pacote_UL_payload = bytearray(Tamanho_pacote)

# ===== Callbacks MQTT =====
def on_connect(client, userdata, flags, reason_code, properties):
    global estado_mqtt
    if reason_code == 0:
        print("[MQTT] Conectado ao Broker MQTT com sucesso.")
        client.subscribe(TOPIC_UL, qos=MQTT_QOS)
        print(f"[MQTT] Inscrito no tópico: {TOPIC_UL} (QoS{MQTT_QOS})")
        estado_mqtt = 1
    else:
        print(f"[MQTT] Falha na conexão. Código: {reason_code}")
        estado_mqtt = 0

def on_publish(client, userdata, mid, reason_code, properties):
    """Confirmação de entrega (PUBACK) do pacote DL publicado em QoS1."""
    #print(f"[MQTT] PUBACK recebido para mid={mid} (pacote DL confirmado pelo broker).")
    pass

def on_message(client, userdata, msg):
    """Callback disparado ao receber pacote UL vindo do ESP32."""
    global Pacote_UL_payload
    payload = msg.payload
    if len(payload) >= Tamanho_pacote:
        Pacote_UL_payload = bytearray(payload[:Tamanho_pacote])
        Pacote_UL_status.set()   # Sinaliza que chegou um pacote válido

def on_disconnect(client, userdata, flags, reason_code, properties):
    global estado_mqtt
    if reason_code != 0:
        print(f"[MQTT] Desconectado inesperadamente (rc={reason_code}). Tentando reconectar...")
        estado_mqtt = 0
        client.reconnect()

# ========================= 2 - Variáveis e arquivos
Pacote_DL = [0]*Tamanho_pacote
PacoteUL  = [0]*Tamanho_pacote

# Caminho da Pasta de armazenamento (Caminho Relativo)
PASTA_ARMAZENAMENTO = os.path.join("..", "4_N4_Armazenamento")

# Caminhos dos arquivos de armazenamento e leitura de parâmetros
caminho_parametros = os.path.join(PASTA_ARMAZENAMENTO, "Parametros")
caminho_dados      = os.path.join(PASTA_ARMAZENAMENTO, "Dados_Brutos")

# Garante que os pacotes de DL e UL estão com valor 0
for i in range(Tamanho_pacote):
   Pacote_DL[i] = 0
   PacoteUL[i]  = 0

# ================== 3 - Arquivos criados para o Nível 4 Armazenamento
# Para gravar arquivo de Log.
#Grava_log = input('0 para não gravar e 1 para gravar = ')
Grava_log = 1

# os.makedirs com exist_ok=True cria toda a estrutura de uma vez
os.makedirs(caminho_dados, exist_ok=True)
os.makedirs(caminho_parametros, exist_ok=True)
caminho_led = os.path.join(caminho_parametros, "cmd_led_amarelo.txt")

Cabecalho = 'Time stamp,Contador,DL_B0,DL_B1,DL_B2,DL_B3,DL_B4,DL_B5,DL_B6,DL_B7,DL_B8,DL_B9,DL_B10,DL_B11,DL_B12,DL_B13,DL_B14,DL_B15,DL_B16,DL_B17,DL_B18,DL_B19,UL_B0,UL_B1,UL_B2,UL_B3,UL_B4,UL_B5,UL_B6,UL_B7,UL_B8,UL_B9,UL_B10,UL_B11,UL_B12,UL_B13,UL_B14,UL_B15,UL_B16,UL_B17,UL_B18,UL_B19'

# ============= INICIALIZAÇÃO
# ===== Inicialização do cliente MQTT =====
client = mqtt.Client(CallbackAPIVersion.VERSION2)
client.on_connect    = on_connect
client.on_message    = on_message
client.on_disconnect = on_disconnect
client.on_publish    = on_publish

print("[MQTT] Conectando ao broker MQTT - porta 1883...")
client.connect(BROKER, PORTA_MQTT, keepalive=60)
client.loop_start()   # Thread de fundo para receber mensagens

# Aguarda conexão ser estabelecida com o BROKER
time.sleep(2)

# =============== Camada de aplicação DL
Comando_LED_amarelo = 0  # Inicia apagado
# ================ Camada de Transporte DL
Contador_pkt_DL = 0
perda_PK_RX     = 0
# ================ Camada de Rede DL
#ID_sensor = input("Identificação do sensor = ")
ID_sensor = 1
#ID_gateway = input ("Identificação do gateway =")
ID_gateway = 0
# ================ Camada MAC DL
Tempo_entre_pacotes = float(input("Tempo entre pacotes (LRC = 1s | SRC = 8s) = ").replace(",", "."))

# ===== Loop principal: repete pedindo número de medidas =====
print("\n========== Gateway LoRa - Comunicação MQTT ==========")
try:
    while True:

      # ----- Entrada do usuário -----
      num_medidas = input("\nEntre com o número de medidas (0 para sair): ").strip()
      if num_medidas == "0":
         print("Encerrando...")
         break
      try:
         medidas = int(num_medidas)
      except ValueError:
         print("Valor inválido. Tente novamente.")
         continue

      # Gera o nome do arquivo de log da rodada
      filename1 = strftime(os.path.join(caminho_dados, "Rodada_Teste_%Y_%m_%d_%H-%M-%S.txt"))
      Log_dados = open(filename1, 'w')
      print("Arquivo de log: %s" % filename1)
      print(Cabecalho, file=Log_dados)

      # Caso MQTT desconectado - Reconectar
      if estado_mqtt != 1:
          client.reconnect()

      Variavel_loop = int(num_medidas) + 1
      # ================ Envio de pacote de DL
      try:
         for j in range(1, int(Variavel_loop)):
      # ===================== LOOP DE ENVIO DE PACOTES =============
            Tempo_inicio_pacote = time.time()
            try:
               # ======== Camada de aplicação PACOTE DL
               # Lê o arquivo cmd_led_amarelo.txt
               with open(caminho_led, "r") as f:
                  linha = f.readline()
                  # Remove espaços e ENTER
                  linha = linha.strip()
                  # Se o valor for 0 ou 1
                  if linha == "0":
                     Comando_LED_amarelo = 0
                  elif linha == "1":
                     Comando_LED_amarelo = 1
                  else:
                     # Qualquer outro conteúdo assume 0
                     Comando_LED_amarelo = 0
            except:
                  # Se houver qualquer erro assume 0
                  Comando_LED_amarelo = 0

            # Coloca o comando no byte 16 do DL
            Pacote_DL[16] = Comando_LED_amarelo
            # ======== Camada de transporte DL
            Contador_pkt_DL = Contador_pkt_DL + 1
            if Contador_pkt_DL == 256:
               Contador_pkt_DL = 0
            Pacote_DL[12] = int(Contador_pkt_DL)
            # ======== Camada de rede DL
            Pacote_DL[8] = ID_sensor
            Pacote_DL[9] = ID_gateway
            # ======== Camada MAC de DL
            Pacote_DL[4] = int(Tempo_entre_pacotes)
            # ======== Camada PHY de DL
            # Publica pacote DL no broker MQTT (QoS1)
            Pacote_UL_status.clear()
            result = client.publish(TOPIC_DL, bytes(Pacote_DL), qos=MQTT_QOS)

            # AGUARDA ACK DO BROKER - QoS1
            if client.is_connected():
               try:
                  # Aguarda confirmação da publicação do Pacote DL pelo retorno do result client.publish(timeout = tempo entre pacotes)
                  result.wait_for_publish(timeout=Tempo_entre_pacotes)
               except RuntimeError as e:
                  print(f"[MQTT Erro] Falha ao aguardar publicação: {e} timeout > tempo entre os pacotes")
                  # Aqui você pode tratar a queda: ex. salvar o pacote ou esperar reconectar
               except Exception as e:
                  print(f"[Erro] Outro erro ocorreu: {e}")
            else:
               print("[MQTT] Não foi possível publicar. Cliente desconectado.")
               # Inserir Lógica de contingência se o cliente já estiver deslogado
               medidas = 0
               client.disconnect()
               print("[MQTT] Reconectando ao broker...")
               client.reconnect()

            # Aguarda tempo de Publicação no BROKER + Tempo Rádio LoRa
            time.sleep(Tempo_entre_pacotes/2)

            # ======== COLETA UPLINK NO BROKER ========
            # Aguarda novo pacote UL publicado pelo Gateway (timeout = Tempo_entre_pacotes)
            Pacote_UL_novo = Pacote_UL_status.wait(timeout=Tempo_entre_pacotes)

            if Pacote_UL_novo:
               Pacote_UL = Pacote_UL_payload
               if len(Pacote_UL) == Tamanho_pacote:
                  print('Pacote = ',j,' | Pacote UL recebido | LED = ',Comando_LED_amarelo)
                  Dados_DL = ''
                  Dados_UL = ''
                  #Prepara os dados dos pacotes de Downlink e Uplink para serem impressos
                  for i in range(Tamanho_pacote):
                     if i == 0:
                        Dados_DL = str(Pacote_DL[i])
                        Dados_UL = str(Pacote_UL[i])
                     else:
                        Dados_DL = Dados_DL + ', ' + str(Pacote_DL[i])
                        Dados_UL = Dados_UL + ', ' + str(Pacote_UL[i])
                  Tempo = time.asctime()
                  print(Tempo + ', ' + str(j) + ', Downlink: ' + Dados_DL + ' Uplink: ' + Dados_UL)
                  # Grava Pacotes
                  if Grava_log == 1:
                     Dados_log = Tempo + ',' + str(j) + ',' + Dados_DL + ',' + Dados_UL
                     print(Dados_log,file=Log_dados)
                     Log_dados.flush()
            else:
               perda_PK_RX += 1
               print('Cont = ', j, ' PERDEU PACOTE ')
               Dados_DL = ''
               Dados_UL = ''
               for i in range(Tamanho_pacote):
                  if i == 0:
                     Dados_DL = str(Pacote_DL[i])
                     Dados_UL = '9'
                  else:
                     Dados_DL = Dados_DL + ', ' + str(Pacote_DL[i])
                     Dados_UL = Dados_UL + ', 9'
               Tempo = time.asctime()
               print(Tempo + ', ' + str(j) + ', Downlink: ' + Dados_DL + ' Uplink: ' + Dados_UL)

               # Grava Pacotes
               if Grava_log == 1:
                  Dados_log = Tempo + ',' + str(j) + ',' + Dados_DL + ',' + Dados_UL
                  print(Dados_log,file=Log_dados)
                  Log_dados.flush()

            Tempo_gasto = time.time() - Tempo_inicio_pacote
            if Tempo_gasto < Tempo_entre_pacotes:
               time.sleep(Tempo_entre_pacotes - Tempo_gasto)

         print('Pacotes enviados = ',j,' Pacotes perdidos = ',perda_PK_RX)
         if Grava_log == 1:
            Log_dados.close()
         print('[LoRa] Fim da Execução')

      except:
         if Grava_log == 1:
            Log_dados.close()
         print('[LoRa] Fim da Execução')

# Interrompe a aplicação N2_N3 e a conexão com MQTT
except KeyboardInterrupt:
   print("\n[Ctrl + C] Interrompido pelo usuário.")
   try:
      if Grava_log == 1 and not Log_dados.closed:
         Log_dados.close()
   except NameError:
      pass
   print('[LoRa] Fim da Execução')
finally:
   client.loop_stop()
   client.disconnect()
   print("[MQTT] Desconectado do broker.")
