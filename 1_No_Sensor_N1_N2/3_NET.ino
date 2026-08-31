// ====== CAMADA DE REDE DE DL
void Net_radio_receive_DL() {
  if(PacoteDL[8] == ID_sensor) {  // Checa se o pacote de DL é endereçado para o sensor com ID_Sensor correto
  ID_gateway = PacoteDL[9]; // O pacote de DL tem o endereço do gateway no byte 10

  //============== CHAMA A CAMADA DE TRANSPORTE DL
    Transp_radio_receive_DL();
  }
}

// ====== CAMADA DE REDE DE UL
void Net_radio_send_UL() {
// Como o destino do pacote no UL é do nó sensor para o gateway é necessário colocar o ID do gateway e ID do sensor
  PacoteUL[8] = ID_gateway;  
  PacoteUL[9] = ID_sensor;                

//========== CHAMA CAMADA MAC de ul
  Mac_radio_send_UL();
}