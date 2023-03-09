import numpy as np
from math import ceil
import time

HEAD_server_handshake = bytes([9,1,0,0,0,0,0,0,0,0,0,0])

EOP = bytes([1, 2, 3]) 

def atualiza_tempo(tempo_referencia):
    tempo_atual = time.time()
    ref = tempo_atual - tempo_referencia
    return ref

def verifica_eop(head, pacote): # Função para verificar se o payload está correto
    tamanho = head[2] # Tamanho = 3º byte do head = 0
    eop = pacote[12+tamanho:]
    if eop == b'\x01\x02\x03':
        print('Payload recebido com sucesso, esperando próximo pacote')
        return True
    else:
        print('Payload não recebido corretamente')
        return False

def verifica_handshake(head, is_server): # Função para verificar se o handshake está correto
    handshake = head[:2] #Pega os dois primeiros bytes do head
    delta_tempo = 0

    combinado = bytes([9, 1])
    if not is_server:
        combinado = bytes([8, 0])
    while delta_tempo <= 5:
        tempo_atual = time.time()
        if handshake == combinado: 
            print('Handshake realizado com sucesso')
            return True
        delta_tempo = atualiza_tempo(tempo_atual)
    return False


def verifica_ordem(recebido, numero_pacote_atual): # Função usada pelo server para verificar se o pacote está na ordem correta
    head = recebido[:12]
    numero_pacote = head[3] # 4º byte do head = número do pacote
    if numero_pacote == numero_pacote_atual:
        print('Pacote recebido na ordem correta')
        return True
    else:
        print('Pacote recebido fora de ordem')
        return False

def monta_payload(info):
    tamanho = len(info)
    pacotes = ceil(tamanho/50) # 50 é o tamanho máximo do payload
    payloads = []
    for i in range(pacotes):
        if i == pacotes-1:
            payload = info[i*50:tamanho]
            print(f'tamanho do último payload:{len(payload)}')
        else:
            payload = info[i*50:(i+1)*50]
            print(f'tamanho dos payloads intermediários:{len(payload)}')
        payloads.append(payload)
    return payloads

def junta_payloads(lista_payloads, tamanho_info, numero_pacotes): # Função para juntar os payloads em um único array e verificar se o número está correto
    info_total = b''
    for payload in lista_payloads:
        info_total += payload
    
    if numero_pacotes == tamanho_info:
        return True
    else:
        return False

def trata_head(head):
    tamanho_payload = head[2]
    numero_pacote = head[3]
    numero_total_pacotes = head[4]

    return tamanho_payload, numero_pacote, numero_total_pacotes

def trata_pacote(pacote):
    tamanho_pacote = len(pacote)
    head = pacote[:12]
    tamanho = head[2]
    payload = pacote[12:12+tamanho]
    eop = pacote[12+tamanho:]

    return head, payload, eop

def monta_head(h0, h1, h2, h3, h4, h5, h6, h7):
    '''
        Parametros:
        h0 - Tipo de mensagem.
        h1 - Se tipo for 1: número do servidor. Qualquer outro tipo: livre
        h2 - Livre.
        h3 - Número total de pacotes do arquivo.
        h4 - Número do pacote sendo enviado.
        h5 - Se tipo for handshake: id do arquivo (crie um para cada arquivo). Se tipo for dados: tamanho do payload.
        h6 - Pacote solicitado para recomeço quando a erro no envio.
        h7 - Ùltimo pacote recebido com sucesso.
        h8 - h9 - CRC (Por ora deixe em branco. Fará parte do projeto 5).
    '''
    head = bytes([h0, h1, h2, h3, h4, h5, h6, h7, 0, 0])
    return head
