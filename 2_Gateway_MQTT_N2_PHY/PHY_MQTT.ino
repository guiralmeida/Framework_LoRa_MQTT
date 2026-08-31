/*
//  MoT LoRa | Gateway | WissTek IoT | Framework LoRa MQTT
//
//  Versão MQTT com QoS1: comunicação Python N2_N3 ↔ Gateway PKLoRa via broker.hivemq.com
//  - Mantém toda a camada de rádio LoRa (RFM95) do Framework Basic
//  - Substitui USB/Serial por Wi-Fi + MQTT
//  - Usa a biblioteca MQTT by Joel Gaehwiler Vs. 2.5.3 (MQTT.h) para suportar QoS1 (MQTT com ACK)
//
//  Tópicos Publicados no Broker MQTT - broker.hivemq.com
//
//  - DL: assina "mot_lora_SEU_NOME/gateway/downlink"  
//    Gateway LoRa ← realiza leitura via Broker MQTT da publicação do Tópico de Downlink do Python
//
//  - UL: publica em "mot_lora_SEU_NOME/gateway/uplink"
//    Gateway → publica Tópico de Uplink ao Broker MQTT - Python N2_N3 realiza a leitura
//
//
//  Última Modificação: Branquinho / Felipe / Luís Felipe / Anderson / Guilherme - 10/08/2026
*/

// ========================= PACOTE DOWNLINK ==========================
// Recebe pacote DL do broker MQTT (publicado pelo Python)
void Phy_mqtt_receive_DL() {

  if (mqtt_dl_disponivel) {          // Flag setada no callback MQTT
    mqtt_dl_disponivel = false;

    // Copia payload recebido para PacoteDL
    for (int i = 0; i < Tamanho_pacote; i++) {
      PacoteDL[i] = mqtt_dl_payload[i];
    }
    ID_gateway = PacoteDL[10];       // Identifica o gateway

    Serial.println("[PHY] Pacote DL recebido via MQTT.");

    // Chama camada física para transmitir pelo rádio RFM95
    Phy_radio_send_DL();
  }
}

// ==================== ENVIA PACOTE DL PELO RÁDIO RFM95 ==============
// (sem alterações em relação à versão serial)
void Phy_radio_send_DL() {

  // Pisca LED Vermelho → TX para nó sensor
  digitalWrite(LED_VERMELHO_PIN, HIGH);

  LoRa.beginPacket();
  for (int i = 0; i < Tamanho_pacote; i++) {
    LoRa.write(PacoteDL[i]);
  }
  LoRa.endPacket();

  delay(50);
  digitalWrite(LED_VERMELHO_PIN, LOW);
}

// ==================== RECEBE PACOTE UL DO RÁDIO RFM95 ==============
// (sem alterações em relação à versão serial)
void Phy_radio_receive_UL() {

  uint8_t packetSize = LoRa.parsePacket();
  if (packetSize > 0) {
    if (packetSize >= Tamanho_pacote) {
      
      // Pisca LED Verde → RX confirmado
      digitalWrite(LED_VERDE_PIN, HIGH);
      
      for (int i = 0; i < Tamanho_pacote; i++) {
        PacoteUL[i] = LoRa.read();
      }

      RSSI_dBm_UL = LoRa.packetRssi();
      SNR_UL      = LoRa.packetSnr();
      Serial.println(SNR_UL);

      delay(50);
      digitalWrite(LED_VERDE_PIN, LOW);

      // Chama função de envio UL agora via MQTT
      Phy_mqtt_send_UL();
    }
  }
}

// ==================== PUBLICA PACOTE UL NO BROKER MQTT ==============
// Substitui Phy_serial_send_UL(): envia o pacote UL ao Python via MQTT
void Phy_mqtt_send_UL() {

  // --- Mapeia RSSI_UL para 1 byte (mesma lógica da versão serial) ---
  if (RSSI_dBm_UL > -10.5) {
    RSSI_UL = 127;
  } else if (RSSI_dBm_UL <= -10.5 && RSSI_dBm_UL >= -74) {
    RSSI_UL = (int)((RSSI_dBm_UL + 74) * 2);
  } else {
    RSSI_UL = (int)(((RSSI_dBm_UL + 74) * 2) + 256);
  }

  // 1. Trava o valor entre -30 e +30 para evitar que o byte estoure
  if (SNR_UL < -30.0) SNR_UL = -30.0;
  if (SNR_UL > 30.0) SNR_UL = 30.0;

  // Usamos uint8_t (byte) para ocupar apenas 1 byte na memória.
  // Usamos a função round() para garantir que o número float seja 
  // arredondado corretamente antes de virar inteiro.
  SNR_UL_inteiro = (uint8_t)round((SNR_UL + 30.0) * 4.0); // Offset de 30.0dB e passo de 0.25dB (* 4.0)

  // --- Armazena informações de gerência no pacote UL ---
  PacoteUL[2] = RSSI_UL;
  //SNR_UL      = SNR_UL * 100;
  //SNR_UL_inteiro = (int)SNR_UL;
  PacoteUL[3] = (byte)SNR_UL_inteiro;

  // --- Publica os 20 bytes no tópico UL, com QoS1 (at least once) ---
  // Importante para o dado de luminosidade, que é a peça central do framework:
  // o broker confirma (PUBACK) e a biblioteca retransmite se necessário.
  if (mqttClient.connected()) {
    bool ok = mqttClient.publish(TOPIC_UL, (char*)PacoteUL, Tamanho_pacote, false, MQTT_QOS);
    if (ok) {
      Serial.println("[PHY] Pacote UL publicado via MQTT (QoS1).");
    } else {
      Serial.println("[PHY] Falha ao publicar pacote UL via MQTT.");
    }
  } else {
    Serial.println("[PHY] MQTT desconectado – pacote UL descartado.");
  }

}


// =====================================================================
//                     Callback MQTT (recepção de mensagens)
// =====================================================================
// Callback "advanced" -- necessário para acessar o payload como bytes
// binários (o callback simples da lib entrega String, que corrompe
// bytes nulos/binários). Nunca chamar publish/subscribe aqui dentro
// (recomendação da própria biblioteca) -- só seta a flag.
void mqtt_callback(MQTTClient *client, char topic[], char bytes[], int length) {
  if (strcmp(topic, TOPIC_DL) == 0) {
    if (length >= Tamanho_pacote) {
      for (int i = 0; i < Tamanho_pacote; i++) {
        mqtt_dl_payload[i] = (byte)bytes[i];
      }
      mqtt_dl_disponivel = true;   // sinaliza para o loop principal
    }
  }
}


// =====================================================================
//                    Funções de conexão MQTT
// =====================================================================

void conectar_mqtt() {
  while (!mqttClient.connected()) {
    Serial.print("[MQTT] Conectando ao broker...");
    if (mqttClient.connect(CLIENT_ID.c_str())) {
      Serial.println(" conectado!");
      mqttClient.subscribe(TOPIC_DL, MQTT_QOS);
      Serial.print("[MQTT] Inscrito (QoS");
      Serial.print(MQTT_QOS);
      Serial.print(") em: ");
      Serial.println(TOPIC_DL);
    } else {
      Serial.print(" falhou (erro=");
      Serial.print((int)mqttClient.lastError());
      Serial.println("). Tentando em 3s...");
      delay(3000);
    }
  }
}
