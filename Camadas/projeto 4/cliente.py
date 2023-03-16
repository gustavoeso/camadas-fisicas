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
from timer_error import *

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411"  # Mac    (variacao de)
serialName = "COM4"                    # Windows(variacao de)

'''
    Parametros:
    h0 - Tipo de mensagem.
    h1 - Se tipo for 1: número do servidor. Qualquer outro tipo: livre
    h2 - Livre.
    h3 - Número total de pacotes do arquivo.
    h4 - Número do pacote sendo enviado.
    h5 - Se tipo for handshake: id do arquivo (crie um para cada arquivo). Se tipo for dados: tamanho do payload.
    h6 - Pacote solicitado para recomeço quando a erro no envio.
    h7 - Ultimo pacote recebido com sucesso. (1 se foi sucesso 0 se nao)
    h8:h9 - CRC (Por ora deixe em branco. Fará parte do projeto 5).

Bytes de EOP: (4 bytes de tamanho) - Serve para indicar o fim da mensagem

    1 byte - b'\xAA'
    2 byte - b'\xBB'
    3 byte - b'\xCC'
    4 byte - b'\xDD'

'''

#Tipos de mensagem
TIPO_1 = 1 #chamado do cleinte enviando ao servidor convidando-o para a transmissão
TIPO_2 = 2 #Envio do servidor para o cliente confirmando a transmissão após mensagem do tipo 1
TIPO_3 = 3 #Mensagem de dados
TIPO_4 = 4 #Mensagem do servidor para o cleinte toda vez que uma mensagem tipo 3 é recebida pelo servidor e averiguada
TIPO_5 = 5 #Mensagem de time out
TIPO_6 = 6 #Mensagem de erro

EOP = b'\xAA\xBB\xCC\xDD'

AQRUIVO_LOG = 'client1.txt'
ARQUIVO_ID = 1
SERVER_ID = 1

def main():
    try:
        com1 = enlace(serialName)
        com1.enable()
        print("Abriu a comunicação")

        img = 'Projeto4/img/picara.jpg'
        imgLida = open(img, 'rb').read()
        lista_payload = monta_payload(imgLida) # Lista de payloads da imagem divida
        HEAD_handshake = monta_head(TIPO_1, SERVER_ID, 0, len(lista_payload), 0, ARQUIVO_ID, 0, 0)
        client_handshake = np.asarray(HEAD_handshake + EOP)

        # Enviando bit de sacrifício
        com1.sendData(b'00') 
        time.sleep(0.1)

        try_connection = 'S'

        while True:
            try:
                # Enviando handshake
                com1.sendData(client_handshake)
                time.sleep(0.1)
                print('Handshake enviado.')
                loop_handshake = True
                reenvio = False
                
                timer1 = time.time()
                if not reenvio:
                    log_write(AQRUIVO_LOG, 'envio', 1, 14)
                    timer2 = time.time()
                else:
                    reenvio = False
                    log_write(AQRUIVO_LOG, 'reenvio', 1, 14)
                    
                # Recebendo a resposta do servidor
                while loop_handshake:
                    HEAD_server, _ = com1.getData(10, timer1, timer2)
                    EOP_server_handshake, _ = com1.getData(4, timer1, timer2)
                    print('Head do server recebido.')

                    resposta_servidor = HEAD_server[0]

                    if resposta_servidor == b'\x02' and EOP_server_handshake == EOP:
                        print(f'Handshake correto, a resposta do server e valida.')
                        loop_handshake = False
                    else:
                        com1.sendData(client_handshake)
                        print(f'Handshake incorreto, a resposta do server e invalida.')

            except Exception as erro:
                print("ops! :-\\")
                print(erro)
                com1.disable()
                

            pacote_atual = 1
            for payload in lista_payload:
                HEAD_conteudo_cliente = monta_head(TIPO_3, 0, 0, len(lista_payload), pacote_atual, len(payload), pacote_atual, pacote_atual-1)
                pacote = HEAD_conteudo_cliente + payload + EOP
                com1.sendData(np.asarray(pacote))
                pacote_atual += 1
                
                feedback_client, _ = com1.getDataNormal(1)

                tempo_inicial = time.time()
                if time.time() - tempo_inicial > 5:
                    resposta = print('Servidor inativo, reenviando ' + '\n')
                    com1.sendData(np.asarray(pacote))
                    
                    tempo_inicial = time.time()
                    if time.time() - tempo_inicial > 5:
                        print('Servidor inativo, desativando comunicação.')
                        com1.disable(); return


                time.sleep(0.1)
                if feedback_client == 1:
                    print(f'Tamanho do payload incorreto {pacote_atual}, reenvie o pacote.')
                    com1.disable(); return
                if feedback_client == 2:
                    print(f'Pacote {pacote_atual} enviado com sucesso.')
                com1.rx.clearBuffer()
                time.sleep(0.1)
            
            HEAD_server_final, _ = com1.getData(14) # Recebendo o head do servidor
            is_trasmission_ok = (HEAD_server_final[4] == 1)
            eop_server_final, _ = com1.getData(3) # Recebendo o EOP do servidor
            pacote_server_final = HEAD_server_final + eop_server_final
            is_eop_server_final_correct = verifica_eop(HEAD_server_final, pacote_server_final)

            if not is_trasmission_ok:
                print('Erro no envio de pacotes. Encerrando conexão.')
            if is_trasmission_ok and is_eop_server_final_correct:
                print('Transmissão finalizada com sucesso.')
            
            print('-----------------------------------------')
            print('Comunicação Encerrada')
            print('-----------------------------------------')
            com1.disable()


                # com1.rx.clearBuffer()
                # tempo_agora = time.time()
                # while (com1.rx.getIsEmpty()) and (atualiza_tempo(tempo_agora) < 5):
                #     pass
                # if com1.rx.getIsEmpty():
                #     try_connection = str(input('Servidor Inativo. Tentar novamente? (S/N) ')).upper()
                #     if try_connection == 'S':
                #         com1.sendData(b'00') # Enviando bit de sacrifício
                #         time.sleep(0.1)
                #         com1.sendData(client_handshake) # Enviando handshake
                #         time.sleep(0.1)
                #     if try_connection == 'N':
                #         print('Servidor Inativo. Encerrando conexão.')
                #         com1.disable(); return
                # else:
                #     server_handshake, _ = com1.getData(14)
                #     tipo_mensagem = server_handshake[0]
                #     if server_handshake != b'x02': 
                #         print('Handshake incorreto. Encerrando conexão.')
                #         com1.disable(); return
                #     if server_handshake == b'x02':
                #         print('Handshake server está correto.')
                #         break
    
        # Condições para encerrar a conexão

    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        
    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
