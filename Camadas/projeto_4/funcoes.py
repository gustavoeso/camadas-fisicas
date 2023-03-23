import numpy as np
from math import ceil
import time
from datetime import datetime
from crccheck.crc import Crc16


def monta_payload(info):
    tamanho = len(info)
    pacotes = ceil(tamanho/114) # 50 é o tamanho máximo do payload
    payloads = []
    for i in range(pacotes):
        if i == pacotes-1:
            payload = info[i*114:tamanho]
            print(f'tamanho do último payload:{len(payload)}')
        else:
            payload = info[i*114:(i+1)*114]
            print(f'tamanho dos payloads intermediários:{len(payload)}')
        payloads.append(payload)
    return payloads


def monta_head_handshake(h0, h1, h2, h3, h4, h5, h6, h7):
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
    '''
    head = bytes([h0, h1, h2, h3, h4, h5, h6, h7, 0, 0])
    return head


def monta_head(h0, h1, h2, h3, h4, h5, h6, h7, payload):
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
    '''

    crc = Crc16().calc(payload)
    crc = int.to_bytes(crc, 2, byteorder='big')
    crc1 = crc[0]
    crc2 = crc[1]

    head = bytes([h0, h1, h2, h3, h4, h5, h6, h7, crc1, crc2])
    return head


def log_write(arquivo:str, operacao:str, tipo:int, tamanho:int, pacote_enviado:int=None, total_pacotes:int=None):
    '''
    Função para escrever os logs em um arquivo txt.

    Parâmetros:
        arquivo: Nome do arquivo em que o log será escrito.
        op : String indicando a operação que está sendo feita (Envio, recebimento ou reenvio)
        tipo : Número do tipo do pacote.
        tamanho_bytes : Número do tamanho do payload da mensagem.
        pacote_enviado : Número do pacote (é incrementado durante a transmissão).
        total_pacotes : Número total de pacotes que serão enviados na transmissão que está sendo realizada.
    '''
    if not total_pacotes:
        total_pacotes = ''
    if not pacote_enviado:
        pacote_enviado = ''
    
    with open(f'projeto_4/logs/{arquivo}', 'a') as f:
        conteudo = f'{datetime.now()} /{operacao}/Tipo:{tipo}/Tamanho:{tamanho}/Num_pacote:{pacote_enviado}/TotalPacotes:{total_pacotes} \n'
        f.write(conteudo)
