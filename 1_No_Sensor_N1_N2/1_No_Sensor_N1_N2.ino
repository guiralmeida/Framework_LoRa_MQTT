/*
  MoT LoRa | Nó Sensor | WissTek IoT | Framework LoRa
  Última versão: Branquinho, Felipe, Anderson, Luís Felipe e Guilherme (Adaptado para ESP32 - Kit PK-LORa) - 31/08/2026
*/

//=======================================================================
//                     1 - Bibliotecas
//=======================================================================
#include <SPI.h> // A SPI é usada para conectar o ESP32 com o RFM95
#include <LoRa.h> // Biblioteca do RFM95

//=======================================================================
//                     2 - Variáveis e Mapeamento
//=======================================================================

// ============= Pinagem na placa da PK-LoRa da ligação do RFM95 com o ESP32
#define SCK_PIN    5
#define MISO_PIN  19
#define MOSI_PIN  27
#define NSS_PIN   18
#define RST_PIN   14
#define DIO0_PIN  26

// ============= CAMADA FÍSICA
// Parâmetros do LoRa
#define FREQUENCY_IN_HZ       903E6     // Frequência de operação
#define txPower               17        // Potência de transmissão 17 dBm
#define spreadingFactor       7         // Configuração SRC = 7   |  LRC=12
#define signalBandwidth       500E3     // Configuração SRC = 500E3  |  LRC=125E3
#define codingRateDenominator 5         // Configuração SRC = 5   |  LRC=8

// Váriáveis utilizadas no código
int RSSI_dBm_DL; // Variável com a potência rádio recebida (RSSI) em dBm
int RSSI_DL;     // Variável de mapeamento da RSSI em um valor de 0 a 255 para colocar no pacote
float SNR_DL;    // Variável com a relação sinal ruído
uint8_t SNR_DL_inteiro; // Variável inteira para enviar a SNR, que será convertida para a SNR original no Python

// ============== CAMADA MAC
#define Tamanho_pacote 20
byte PacoteDL[Tamanho_pacote];
byte PacoteUL[Tamanho_pacote];

// ============= CAMADA DE REDE
// Identificação do sensor e tamanho de pacote
int ID_sensor = 1; // Variável de iIdentificação do sensor que está no pacote de DL byte 8
int ID_gateway;    // Variável com o ID_gateway que estará no pacote de DL byte 10

// ============== CAMADA DE TRANSPORTE
int contador_pkt_DL = 0; // Variável para o contador de pacotes de DL
int contador_pkt_UL = 0; // Variável para o contador de pacotes de UL

// ============= CAMADA DE APLICAÇÃO
// Pinos da PK-LoRa
// Pinos dos LEDs
#define LED_VERMELHO_PIN 15
#define LED_AMARELO_PIN   2
#define LED_VERDE_PIN     4

// Pinos de Entradas Analógicas
#define LDR_PIN 36   // ADC1_CH0 — sensor LDR - PIN VP
int luminosidade; // Variável que vai receber o valor da luminosidade entre 0 e 4095 - ADC 12 bits

// Pino do botão
#define BOTAO_PIN  39   // Pino do Botão - PIN VN

//=======================================================================
//                     3 - Setup de inicialização
//=======================================================================
void setup() {
  Serial.begin(115200);
  //while (!Serial);

  Serial.println("--- Iniciando Nó Sensor ---");

  // --- Inicialização de I/O ---
  pinMode(LED_VERMELHO_PIN, OUTPUT);
  pinMode(LED_AMARELO_PIN, OUTPUT);
  pinMode(LED_VERDE_PIN, OUTPUT);
  
  // Garante que os LEDs iniciem desligados
  digitalWrite(LED_VERMELHO_PIN, LOW);
  digitalWrite(LED_AMARELO_PIN, LOW);
  digitalWrite(LED_VERDE_PIN, LOW);

  // resistores de pull-up/pull-down internos. O seu hardware precisa garantir isso.
  pinMode(BOTAO_PIN, INPUT); 

  // --- Inicialização Módulo RF95 (LoRa) ---
  
  // 1. Remapeia e inicializa o barramento SPI com os pinos do seu Kit
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, NSS_PIN);

  // 2. Informa à biblioteca LoRa os pinos de controle
  LoRa.setPins(NSS_PIN, RST_PIN, DIO0_PIN);

  if (!LoRa.begin(FREQUENCY_IN_HZ)) {
    Serial.println("Erro ao iniciar módulo RFM95");
  }
  //LoRa.begin(FREQUENCY_IN_HZ));
  LoRa.setTxPower(txPower);
  LoRa.setSpreadingFactor(spreadingFactor);
  LoRa.setSignalBandwidth(signalBandwidth);
  LoRa.setCodingRate4(codingRateDenominator);
  Serial.println("LoRa Inicializado com Sucesso!");
  
  // Pisca o LED Verde para indicar inicialização bem-sucedida
  digitalWrite(LED_VERDE_PIN, HIGH);
  delay(1000);
  digitalWrite(LED_VERDE_PIN, LOW);
}

//=======================================================================
//                     4 - Loop de repetição
//=======================================================================
void loop() {
  // Função que recebe pacote de DL
  Phy_radio_receive_DL(); 
}