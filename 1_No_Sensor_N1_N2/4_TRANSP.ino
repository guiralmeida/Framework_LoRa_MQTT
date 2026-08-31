//================ CAMADA DE TRANSPORT DL ========
void Transp_radio_receive_DL() { 
  // Faz o controle fluzo entre o nó sensor e o gateway
  // Por exemplo contagem de pacotes recedidos de DL
  contador_pkt_DL = contador_pkt_DL + 1;

  //============== CHAMA A CAMADA DE APLICAÇÃO DE DL
  App_radio_receive_DL();
}

//================ CAMADA DE TRANSPORTE DE UL ========
void Transp_radio_send_UL() { 
  // Aloca no pacote de UL o valor contador de pacotes de DL
  PacoteUL[12] = (contador_pkt_DL/256);
  PacoteUL[13] = (contador_pkt_DL%256);
  
  contador_pkt_UL = contador_pkt_UL + 1;
  PacoteUL[14] = (contador_pkt_UL/256);
  PacoteUL[15] = (contador_pkt_UL%256);

//============ CHAMA A CAMADA DE REDE DE UL
  Net_radio_send_UL();
}
