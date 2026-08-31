//================ CAMADA MAC DL ========
void Mac_radio_receive_DL() { 
  // No pacote MOT são os bytes 4, 5, 6, 7 do DL, que serão utilizados para alguma função de MAC
  // Um exemplo é o comando para o nó sensor dormir e o tempo que ele vai dormir
  
  // =========== CHAMA A CAMADA DE REDE NET DL
  Net_radio_receive_DL();
}

//================ CAMADA MAC UL ========
void Mac_radio_send_UL() {
  // Pode passar na MAC o status do sleep
 
  //============ CHAMA CAMADA FÍSICA UL
  Phy_radio_send_UL();
}
