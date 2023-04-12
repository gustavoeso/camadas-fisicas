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
from crccheck import *

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

AQRUIVO_LOG = 'cliente3.txt'
ARQUIVO_ID = 1
SERVER_ID = 1

def main():
    try:
        com1 = enlace(serialName)
        com1.enable()
        print("Abriu a comunicação")

        # img = 'G:\My Drive\Insper\Semestre 4\camadas-fisicas\Camadas\projeto 4\img\picara.jpg'
        img = 'projeto_4\img\picara.jpg'
        imgLida = open(img, 'rb').read()
        lista_payload = monta_payload(imgLida) # Lista de payloads da imagem divida
        HEAD_handshake = monta_head_handshake(TIPO_1, SERVER_ID, 0, len(lista_payload), 0, ARQUIVO_ID, 0, 0)
        client_handshake = np.asarray(HEAD_handshake + EOP)

        # Enviando bit de sacrifício
        com1.sendData(b'00') 
        time.sleep(0.1)

        inicia = False

        # Recebendo a resposta do servidor
        while not inicia:
            # Enviando handshake
            com1.sendData(client_handshake)
            log_write(AQRUIVO_LOG, 'envio', 1, 14)
            print('Handshake enviado.')
            time.sleep(5)

            HEAD_server, _ = com1.getDataNormal(10)
            EOP_server_handshake, _ = com1.getDataNormal(4)
            log_write(AQRUIVO_LOG, 'recebimento', 2, 14)
            print('Head do server recebido.')

            resposta_servidor = HEAD_server[0]
            print(HEAD_server)
            print(EOP_server_handshake)

            if resposta_servidor == 2 and EOP_server_handshake == EOP:
                print(f'Handshake correto, a resposta do server e valida.')
                inicia = True
            else:
                print(f'Handshake incorreto, a resposta do server e invalida.')
                inicia = False


        pacote_atual = 1
        reenvio = False
        while pacote_atual <= len(lista_payload):
            try:
                tamanho_payload = len(lista_payload[pacote_atual - 1])
                tamanho_total = len(lista_payload)
                payload_atual = lista_payload[pacote_atual-1]
                HEAD_conteudo_cliente = monta_head(TIPO_3, 0, 0, tamanho_total, pacote_atual, tamanho_payload, pacote_atual, pacote_atual-1, payload_atual)
                pacote = HEAD_conteudo_cliente + payload_atual + EOP
                com1.sendData(np.asarray(pacote))
                log_write(AQRUIVO_LOG, 'envio', 3, tamanho_payload + 14, pacote_atual, tamanho_total)
                time.sleep(0.5)

                timer1 = time.time()
                if not reenvio:
                    timer2 = time.time()


                feedback_client, _ = com1.getData(14, timer1, timer2)
                resposta_servidor_tipo = feedback_client[0]
                log_write(AQRUIVO_LOG, 'recebimento', resposta_servidor_tipo, 14)
                pacote_servidor = feedback_client[6]
                print(feedback_client)

                if resposta_servidor_tipo == 4:
                    print(f'Pacote {pacote_atual} recebido com sucesso.')
                    pacote_atual += 1
                    reenvio = False


                elif resposta_servidor_tipo == 6:
                    pacote_servidor = feedback_client[6]
                    print(f' numero do pacote incorreto, pacote correto de acordo com o servidor: {pacote_servidor}')
                    pacote_atual = pacote_servidor
                    com1.rx.clearBuffer()
                    reenvio = False

            except Timer1Error:
                reenvio = True

            except Timer2Error:
                print('Time out, servidor inativo.')
                HEAD_tipo5 = monta_head(TIPO_5, 0, 0, 0, 0, 0, 0, 0)
                pacote_tipo5 = HEAD_tipo5 + EOP
                com1.sendData(np.asarray(pacote_tipo5))
                log_write(AQRUIVO_LOG, 'envio', 5, 14)
                time.sleep(0.5)
                com1.disable(); return

        

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
