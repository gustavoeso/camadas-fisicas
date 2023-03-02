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


        # Head para verificar se o server está vivo
        Head_handshake = bytearray([0,0,0,0,0,0,0,0,0,0,0,9])

        #EOP para verificar se o server está vivo
        eop = bytearray([1,2,3])

        #enviando Head+EOP
        com1.sendData(Head_handshake + eop)

        print('Aguardando resposta do servidor...')

        tempo_inicial = time.time()
        while com1.rx.getIsEmpty():
            if time.time() - tempo_inicial > 5:
                resposta = input('Servidor inativo. Tentar novamente? S/N?' + '\n')
                if resposta == 'S':
                    com1.sendData(Head_handshake + eop)
                    print('Aguardando resposta do servidor...')
                    tempo_inicial = time.time()
                elif resposta == 'N':
                    com1.disable()
                    break
                else:
                    ('Resposta inválida. Encerrando comunicação.')
                    com1.disable()
                    break

        else:
            rxBuffer, nRx = com1.getData(12)
            print(f'Server recebeu o pacote {rxBuffer}')
            if rxBuffer != b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t':
                print('ERRO: Servidor não recebeu o pacote correto.')
                com1.disable()
            else:
                print('Handshake realizado com sucesso.')
            
        imageR = "G:/My Drive/Insper/Semestre 4/camadas-fisicas/Camadas/projeto 3/img/picara.png"

        txBuffer = open(imageR, 'rb').read()
        print("meu array de bytes tem tamanho {}" .format(len(txBuffer)))

        bytes1 = len(txBuffer)
        contador = 0
        pacotes = []
        while bytes1 >= 50:
            pacotes.append(txBuffer[contador:contador+50])
            contador += 50
            bytes1 -= 50
        
        pacotes.append(txBuffer[contador:])
        
        pacote_atual = 0
        for pacote in pacotes:
            pacote_atual += 1
            n_pacotes = len(pacotes)
            n_bytes = len(pacote)
            head = bytearray([pacote_atual,n_pacotes,n_bytes,0,0,0,0,0,0,0,0,0])
            com1.sendData(head + pacote + eop)
            print(f'Pacote {pacote_atual} enviado com sucesso. numero de bytes no pacote {n_bytes}')

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
