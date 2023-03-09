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
from funcoes import *
from operator import truediv


# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM4"                  # Windows(variacao de)


'''
Informações do Head: (12 bytes de tamanho) - Serve para passar informações sobre a msg que será enviada

    1 byte - tipo de mensagem  - b'\x01' - Tamanho do payload incorreto, b'\x02' - Tamanho do payload correto
    2 byte - Verifica handshake 
    3 byte - Numero de bytes do payload
    4 .. 12 byte - placeholders

Bytes de EOP: (3 bytes de tamanho) - Serve para indicar o fim da mensagem

    1 byte - b'\x01'
    2 byte - b'\x02'
    3 byte - b'\x03'
'''

HEAD_server_handshake = bytes([9,1,0,0,0,0,0,0,0,0,0,0])

EOP = bytes([1, 2, 3]) 

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

        # Esperando byte de sacrifício
        print("esperando 1 byte de sacrifício")
        rxBuffer, nRx = com1.getData(1)
        com1.rx.clearBuffer() # Limpa o buffer de recebimento para receber os comandos
        time.sleep(0.1)
        print('byte de sacrifício recebido')	

        HEAD_client_handshake, _ = com1.getData(12)
        time.sleep(0.1)
        is_handshake_correct = verifica_handshake(HEAD_client_handshake, False)
        total_packages = HEAD_client_handshake[4]

        if is_handshake_correct:
            tamanho_payload = int(HEAD_client_handshake[2])
            resto_handshake_client, _ = com1.getData(tamanho_payload+3)
            time.sleep(0.1)
            handshake_client = HEAD_client_handshake + resto_handshake_client
            verificacao_eop = verifica_eop(HEAD_client_handshake, handshake_client)
            if not verificacao_eop:
                return
            else:
                handshake_server = np.asarray(HEAD_server_handshake + EOP)
                com1.sendData(handshake_server)
                time.sleep(0.1)
                print("Handshake do servidor enviado")

        img_recebida = b''
        pacote_antes = 1
        pacotes_recebidos = 0

        while True:
            HEAD_client, _ = com1.getData(12)
            time.sleep(0.5)
            tamanho_payload, pacote_atual, _ = trata_head(HEAD_client)
            # Forçando erro no tamanho do payload
            tamanho_payload += 1 
            if pacote_atual != pacote_antes:
                print("Pacote recebido fora de ordem")
                HEAD_server = bytes([1,0,0,0,0,0,0,0,0,0,0,0])
                com1.sendData(HEAD_server + EOP)
                com1.disable(); return
            else:
                HEAD_server = bytes([2,0,0,0,0,0,0,0,0,0,0,0])
                com1.sendData(HEAD_server + EOP)
                time.sleep(0.5)

            pacotes_recebidos += 1
            pacote_antes = pacote_atual

            resto_pacote, _ = com1.getData(tamanho_payload+3)
            time.sleep(0.1)

            pacote_client = HEAD_client + resto_pacote
            HEAD_client, payload_client, EOP_client = trata_pacote(pacote_client)
            img_recebida += payload_client 
            
            # Verificando se o eop está no lugar correto
            is_eop_correct = verifica_eop(HEAD_client, pacote_client)
            if not is_eop_correct:
                print("EOP fora do lugar")
                com1.disable(); return
            if pacotes_recebidos == total_packages:
                break
            if pacotes_recebidos != total_packages:
                pacote_antes += 1
        
        HEAD_client_final = bytes([1,0,0,0,0,0,0,0,0,0,0,0])
        if pacotes_recebidos != total_packages:
            print("Pacotes recebidos diferente do total de pacotes")
        else:
            HEAD_client_final = bytes([1,0,0,0,1,0,0,0,0,0,0,0])
            print("Transmissão finalizada com sucesso")
        
        # Envia o pacote final para o cliente
        pacote_final = HEAD_client_final + EOP
        com1.sendData(pacote_final)
        time.sleep(0.5)

        img_recebida_nome = 'Projeto3/img/img_recebida.png'
        print("Salvando imagem recebida")
        with open(img_recebida_nome, 'wb') as f:
            f.write(img_recebida)
            print("Imagem salva com sucesso")
            f.close()

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
