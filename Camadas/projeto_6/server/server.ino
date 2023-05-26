#include <Arduino.h>

int pinServer = 8; 
float baudrate = 9600;
int msg;

void setup() {
  pinMode(pinServer, INPUT);
  Serial.begin(baudrate);
}


void meio_periodo(void){
  for (int i = 0; i < 1093; i++){
    asm("NOP");
  }
}

void periodo(void){
  meio_periodo();
  meio_periodo();
}

void loop() {
  if (digitalRead(pinServer)== 0){
    int q_1s = 0;
    meio_periodo();
    periodo();
    for (int i = 0; i < 8; i++){
      int bitAtual = digitalRead(pinServer); // lê o bit atual
      periodo(); // Deve ser chamado após a leitura de 1 bit
      if (bitAtual == 1){
        q_1s++; // Conta número de bits
      }
      msg |= (bitAtual << i); // Adiciona o bit atual na mensagem
    }
    int bitParidade = digitalRead(pinServer); // lê o bit de paridade
    int bitParidade_msg = (q_1s % 2); // Cálculo do bit de paridade da mensagem 
    if (bitParidade == bitParidade_msg) {
      //Serial.print("Dados Recebidos: ");
      Serial.println(msg);
      //Serial.println("Bit de paridade está correto!");
    } else{
      Serial.println("ERRO, bit de paridade está incorreto");
    }
    delay(1000);
  }
}
