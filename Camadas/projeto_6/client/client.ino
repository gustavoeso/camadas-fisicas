#include <Arduino.h>

byte mensagem = 0xAA; //Mensagem a ser enviada (A)
int mensagemBin = int(mensagem); // Transformando mensagem em inteiro
int clientPin = 8; //Pin a ser utilizado (8)
float baudrate = 9600; //Baudrate fixo em 9600

void setup() {
  pinMode(clientPin, OUTPUT);
  Serial.begin(9600);
  digitalWrite(clientPin, HIGH);
}

// tempo de um clock (T = 1/frequencia)
// Tempo entre cada clock em segundos (T = 1/baudrate)
// numero de clocks ((T/clock) + 1 )

void meio_periodo(void){
  for(int i =0; i< 1093;i++) { asm("NOP");}
}

void periodo(void){
  meio_periodo();
  meio_periodo();
 }



void loop() {
  // put your main code here, to run repeatedly:
  int ums = 0;
  Serial.println("inicio loop");

  digitalWrite(clientPin, 0); //bit de inicialização
  periodo();

  for(int i = 0; i < 8; i++){
    int bitAtual = 1 & (mensagemBin >> i);
    digitalWrite(clientPin, bitAtual);
    if (bitAtual == 1){
      ums++;
    }
    periodo();
  }
  

  int bitParidade = ums % 2;
  digitalWrite(clientPin, bitParidade);
  periodo();

  digitalWrite(clientPin, 1); //bit de parada
  periodo();

  Serial.println(mensagem, HEX);
  delay(2000);
 }
