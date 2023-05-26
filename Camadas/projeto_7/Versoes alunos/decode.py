# Importe todas as bibliotecas
from suaBibSignal import *
import peakutils  # alternativas  #from detect_peaks import *   #import pickle
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import time


# funcao para transformas intensidade acustica em dB, caso queira usar
def todB(s):
    sdB = 10 * np.log10(s)
    return sdB


def main():
    lista = [[697, 1209], [697, 1336], [697, 1477], [770, 1209], [770, 1336], [770, 1477], [852, 1209], [852, 1336],
             [852, 1477], [941, 1336]]
    # *****************************instruções********************************

    # declare um objeto da classe da sua biblioteca de apoio (cedida)
    # algo como:
    signal = signalMeu()

    # voce importou a bilioteca sounddevice como, por exemplo, sd. entao
    # os seguintes parametros devem ser setados:
    if True:
        sd.default.samplerate = 48000  # taxa de amostragem
        sd.default.channels = 2  # numCanais # o numero de canais, tipicamente são 2. Placas com dois canais. Se ocorrer problemas pode tentar com 1. No caso de 2 canais, ao gravar um audio, terá duas listas
        duration = 5  # tempo em segundos que ira aquisitar o sinal acustico captado pelo mic

    # calcule o numero de amostras "numAmostras" que serao feitas (numero de aquisicoes) durante a gracação. Para esse cálculo você deverá utilizar a taxa de amostragem e o tempo de gravação
    numAmostras = int(sd.default.samplerate * duration)
    # faca um print na tela dizendo que a captacao comecará em n segundos. e entao
    # use um time.sleep para a espera
    print("a captacao comecará em 5 segundos.")
    time.sleep(5)
    # Ao seguir, faca um print informando que a gravacao foi inicializada
    print("gravacao inicializada")

    # para gravar, utilize
    audio = sd.rec(int(numAmostras), 48000, channels=1)
    sd.wait()
    print("...     FIM")
    print(audio)
    # analise sua variavel "audio". pode ser um vetor com 1 ou 2 colunas, lista, isso dependerá so seu sistema, drivers etc...
    # extraia a parte que interessa da gravação (as amostras) gravando em uma variável "dados". Isso porque a variável audio pode conter dois canais e outas informações).
    dados = audio[:, 0]
    print('audio', audio)
    print('dados', dados)
    # use a funcao linspace e crie o vetor tempo. Um instante correspondente a cada amostra!
    tempo = np.linspace(0, duration, numAmostras)
    # plot do áudio gravado (dados) vs tempo! Não plote todos os pontos, pois verá apenas uma mancha (freq altas) . 
    signal.plotFFT(dados, 48000)
    plt.show()
    plt.plot(dados, tempo)
    plt.show()
    ## Calcule e plote o Fourier do sinal audio. como saida tem-se a amplitude e as frequencias
    xf, yf = signal.calcFFT(dados, 48000)

    # agora, voce tem os picos da transformada, que te informam quais sao as frequencias mais presentes no sinal. Alguns dos picos devem ser correspondentes às frequencias do DTMF!
    # Para descobrir a tecla pressionada, voce deve extrair os picos e compara-los à tabela DTMF
    # Provavelmente, se tudo deu certo, 2 picos serao PRÓXIMOS aos valores da tabela. Os demais serão picos de ruídos.

    # para extrair os picos, voce deve utilizar a funcao peakutils.indexes(,,)
    # Essa funcao possui como argumentos dois parâmetros importantes: "thres" e "min_dist".
    # "thres" determina a sensibilidade da funcao, ou seja, quao elevado tem que ser o valor do pico para de fato ser considerado um pico
    # "min_dist" é relatico tolerancia. Ele determina quao próximos 2 picos identificados podem estar, ou seja, se a funcao indentificar um pico na posicao 200, por exemplo, só identificara outro a partir do 200+min_dis. Isso evita que varios picos sejam identificados em torno do 200, uma vez que todos sejam provavelmente resultado de pequenas variações de uma unica frequencia a ser identificada.
    # Comece com os valores:
    # printe os picos encontrados!
    index = peakutils.indexes(yf, thres=0.1, min_dist=25)
    print(f"index de picos {index}")  # yf é o resultado da transformada de fourier
    print(f"frequencias de pico {xf[index]}")  # xf é o vetor das frequencias
    # Aqui você deverá tomar o seguinte cuidado: A funcao  peakutils.indexes retorna as POSICOES dos picos. Não os valores das frequências onde ocorrem! Pense a respeito
    frequencias_de_pico = xf[index]
    frequencias_de_pico_sem_ruido = []
    for i in frequencias_de_pico:
        for frequencias in lista:
            for frequencia in frequencias:
                print(f"i {i} frequencia {frequencia}")
                if frequencia+1 >= i and frequencia-1 <= i:
                    print("achou")
                    if frequencia not in frequencias_de_pico_sem_ruido:
                        frequencias_de_pico_sem_ruido.append(frequencia)
    print(f"frequencias de pico sem ruido {frequencias_de_pico_sem_ruido}")
    # encontre na tabela duas frequencias proximas às frequencias de pico encontradas e descubra qual foi a tecla
    # print o valor tecla!!!
    print(f"tecla {lista.index(frequencias_de_pico_sem_ruido)}")
    # Se acertou, parabens! Voce construiu um sistema DTMF

    # Você pode tentar também identificar a tecla de um telefone real! Basta gravar o som emitido pelo seu celular ao pressionar uma tecla.

    # Exiba gráficos do fourier do som gravados


if __name__ == "__main__":
    main()
