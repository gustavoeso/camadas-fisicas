#include <Arduino.h>

byte mensagem = 0x0A; //Mensagem a ser enviada (A)
int mensagemBin = int(mensagem); // Transformando mensagem em inteiro
int clientPin = 8; //Pin a ser utilizado (8)
float baudrate = 9600; //Boudrate fixo em 9600

void setup() {
  // put your setup code here, to run once:
  pinMode(clientPin, OUTPUT);
  Serial.begin(baudrate);
  digitalWrite(clientPin, HIGH);

}

float timeSkipper(float skipTime = 1, float baudrate = 9600, float t_0 = 0) {
  double clock = 1 / (21*pow(10,6)); // f = 21MHz, T = 1 / f
  double T = 1 / baudrate; // tempo entre clocks
  int n_clocks = floor(T / clock) + 1;
  for (int i = 0; i < int(n_clocks * skipTime); i++){
    asm("NOP"); // Espera 
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  int ums = 0;

  digitalWrite(clientPin, 0); //bit de inicialização
  timeSkipper();


  for(int i = 0; i <8; i++){
    int bitAtual = 1 & (mensagemBin >> i);
    digitalWrite(clientPin, bitAtual);
    if (bitAtual == 1){
      ums++;
    }
    timeSkipper();
  }

  int bitParidade = ums % 2;
  digitalWrite(clientPin, bitParidade);
  timeSkipper();

  digitalWrite(clientPin, 1); //bit de parada
  timeSkipper();

  Serial.print("Dado enviado: ");
  Serial.println(mensagem, HEX);
  delay(2000);

}
