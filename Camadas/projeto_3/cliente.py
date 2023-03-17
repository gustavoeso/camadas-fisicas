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
from timeit import repeat
from funcoes import *

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
    1 byte - tipo de mensagem
    2 byte - Verifica handshake 
    3 byte - Numero de bytes do payload
    4 byte - Numero do pacote
    5 byte - Numero total de pacotes
    6 byte - Status da transmissão (1 - OK, 0 - Erro)
    7...12 byte - placeholder

Bytes de EOP: (3 bytes de tamanho) - Serve para indicar o fim da mensagem

    1 byte - b'\x01'
    2 byte - b'\x02'
    3 byte - b'\x03'

'''

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

        img = 'Projeto3/img/picara.jpg'
        imgLida = open(img, 'rb').read()
        lista_payload = monta_payload(imgLida) # Lista de payloads da imagem divida
        HEAD_handshake = bytes([8,0,0,0,len(lista_payload),0,0,0,0,0,0,0]) # Head para handshake
        client_handshake = np.asarray(HEAD_handshake + EOP)

        # Enviando bit de sacrifício
        com1.sendData(b'00') 
        time.sleep(0.1)

        # Enviando handshake
        com1.sendData(client_handshake)
        time.sleep(0.1)

        try_connection = 'S'

        while True:
            com1.rx.clearBuffer()
            tempo_agora = time.time()
            while (com1.rx.getIsEmpty()) and (atualiza_tempo(tempo_agora) < 5):
                pass
            if com1.rx.getIsEmpty():
                try_connection = str(input('Servidor Inativo. Tentar novamente? (S/N) ')).upper()
                if try_connection == 'S':
                    com1.sendData(b'00') # Enviando bit de sacrifício
                    time.sleep(0.1)
                    com1.sendData(client_handshake) # Enviando handshake
                    time.sleep(0.1)
                if try_connection == 'N':
                    print('Servidor Inativo. Encerrando conexão.')
                    com1.disable(); return
            else:
                server_handshake, _ = com1.getData(15)
                is_server_handshake_correct = verifica_handshake(server_handshake, True)
                if is_server_handshake_correct == False:
                    print('Handshake incorreto. Encerrando conexão.')
                    com1.disable(); return
                if is_server_handshake_correct == True:
                    print('Handshake server está correto.')
                    break
                

        pacote_atual = 1
        for payload in lista_payload:
            HEAD_conteudo_cliente = bytes([3,0,len(payload), pacote_atual, len(lista_payload),0,0,0,0,0,0,0])
            pacote = HEAD_conteudo_cliente + payload + EOP
            com1.sendData(np.asarray(pacote))
            pacote_atual += 1

            feedback_client, _ = com1.getData(1)
            time.sleep(0.1)
            if feedback_client == 1:
                print(f'Tamanho do payload incorreto {pacote_atual}, reenvie o pacote.')
                com1.disable(); return
            if feedback_client == 2:
                print(f'Pacote {pacote_atual} enviado com sucesso.')
            com1.rx.clearBuffer()
            time.sleep(0.1)
        
        HEAD_server_final, _ = com1.getData(12) # Recebendo o head do servidor
        is_trasmission_ok = (HEAD_server_final[4] == 1)
        eop_server_final, _ = com1.getData(3) # Recebendo o EOP do servidor
        pacote_server_final = HEAD_server_final + eop_server_final
        is_eop_server_final_correct = verifica_eop(HEAD_server_final, pacote_server_final)

        # Condições para encerrar a conexão
        if not is_trasmission_ok:
            print('Erro no envio de pacotes. Encerrando conexão.')
        if is_trasmission_ok and is_eop_server_final_correct:
            print('Transmissão finalizada com sucesso.')
        
        print('-----------------------------------------')
        print('Comunicação Encerrada')
        print('-----------------------------------------')
        com1.disable()

    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
