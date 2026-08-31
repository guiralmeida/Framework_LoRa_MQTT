//================ CAMADA FÍSICA DL ========
void Phy_radio_receive_DL() {
  uint8_t packetSize = LoRa.parsePacket();

  if (packetSize) {
    if (packetSize >= Tamanho_pacote) { // Checa se o pacote recebido tem o tamanho em bytes da variável TAMANHO_PACOTE
       
      // Pisca LED Verde - Indica Recepção do Nó Sensor          
      digitalWrite(LED_VERDE_PIN, HIGH);

      for (int i = 0; i < Tamanho_pacote; i++) {
        PacoteDL[i] = LoRa.read();  // Faz a leitura do pacote recebido de DL pelo RFM95 pelo ESP32 no vetor PacoteDL
      }

      RSSI_dBm_DL = LoRa.packetRssi(); // Faz a leitura da RSSI medida pelo RFM95 em dBm
      SNR_DL = LoRa.packetSnr();       // Faz a leitura da SNR medida pelo RFM95
      Serial.println(SNR_DL);

      delay(50);
      digitalWrite(LED_VERDE_PIN, LOW);

      //======== CHAMA A CAMADA MAC DL
      Mac_radio_receive_DL(); 
    }
  }
}

//================ CAMADA FÍSICA UL ========
void Phy_radio_send_UL() {

  //--- Bloco que faz adequação da leitura de RSSI para um byte ---
  if(RSSI_dBm_DL > -10.5)  // Caso a RSSI medida esteja acima do valor superior -10,5 dBm
  {
   RSSI_DL = 127; // equivalente a -10,5 dBm 
  }

  if(RSSI_dBm_DL <= -10.5 && RSSI_dBm_DL >= -74) // Caso a RSSI medida esteja no intervalo [-10,5 dBm e -74 dBm]
  {
   RSSI_DL = ((RSSI_dBm_DL +74)*2) ;
  }

  if(RSSI_dBm_DL < -74) // Caso a RSSI medida esteja no intervalo ]-74 dBm e -138 dBm]
  {
   RSSI_DL = (((RSSI_dBm_DL +74)*2)+256) ;
  }

  // =================Informações de gerência do pacote Início da montagem do pacote de UL
  PacoteUL[0] = RSSI_DL;

  // Trava o valor entre -30 e +30 para evitar que o byte estoure
  if (SNR_DL < -30.0) SNR_DL = -30.0;
  if (SNR_DL > 30.0) SNR_DL = 30.0;

  // Usamos uint8_t (byte) para ocupar apenas 1 byte na memória.
  // Usamos a função round() para garantir que o número float seja 
  // arredondado corretamente antes de virar inteiro.
  SNR_DL_inteiro = (uint8_t)round((SNR_DL + 30.0)  * 4.0); // Offset de 30.0dB e passo de 0.25dB (* 4.0)
  PacoteUL[1] = byte(SNR_DL_inteiro);
 
  // ================= TRANMISSÃO DO PACOTE ENVIDADO PELO ESP32 PARA O RFM95
 
  // Pisca o LED Vermelho indicando transmissão de pacote UL (se permitido)
  digitalWrite(LED_VERMELHO_PIN, HIGH);

  LoRa.beginPacket();                 // Inicia o RFM95 que vai transmitir o pacote de 52 bytes
  for (int i = 0; i < Tamanho_pacote; i++) {
    LoRa.write(PacoteUL[i]);          // Envia byte a byte as informações para o RFM95
  }
  LoRa.endPacket();                   // Finaliza o envio do pacote e o RFM95 transmite o pacote para o Gateway
  
  delay(50);
  digitalWrite(LED_VERMELHO_PIN, LOW);

}