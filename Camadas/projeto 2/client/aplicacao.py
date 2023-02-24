#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
import time
import numpy as np
import random

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM4"                  # Windows(variacao de)


comandos = [b'\x00\x00\x00\x00', b'\x00\x00\xAA\x00', b'\xAA\x00\x00', b'\x00\xAA\x00', b'\x00\x00\xAA', b'\x00\xAA', b'\xAA\x00', b'\x00', b'\xFF']

def main():
    try:
        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)


        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")

        time.sleep(.2)
        com1.sendData(b'00')
        time.sleep(1)

        n_random = random.randint(10,30)

        print(f'numero de comandos: {n_random}')

        lista_comandos = []

        for i in range(n_random):
            valor = random.randint(0,8)
            comando = comandos[valor]
            tamanho_comando = bytearray([len(comando)])


            if(i == n_random-1):
                comando += b'\x11'

            lista_comandos.append(tamanho_comando + comando)

        dados = b''.join(lista_comandos)
        txBuffer = bytearray(dados)

        print(f'tamanho do array = {len(txBuffer)} bytes')

        com1.sendData(np.asarray(txBuffer))

        print('Aguardando resposta do servidor...')
        
        tempo_inicial = time.time()
        while com1.rx.getIsEmpty():
            if time.time() - tempo_inicial > 5:
                print('Tempo de resposta do servidor excedido.')
                com1.disable()
                break

        else:
            rxBuffer, nRx = com1.getData(1)
            print(f'Server recebeu = {rxBuffer[0]} comandos')
            if rxBuffer[0] != n_random:
                print('ERRO: Servidor não recebeu todos os comandos.')
                com1.disable()


        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()


    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
