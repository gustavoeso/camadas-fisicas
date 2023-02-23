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

def randomizador(n):
    lista = []
    for i in range(n):
        valor = random.randint(0,8)
        lista.append(valor)
        if len(lista) == 1:
            lista.append(valor)
    return lista

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
                  
        #aqui você deverá gerar os dados a serem transmitidos. 
        #seus dados a serem transmitidos são um array bytes a serem transmitidos. Gere esta lista com o 
        #nome de txBuffer. Esla sempre irá armazenar os dados a serem enviados.
        
        #faça aqui uma conferência do tamanho do seu txBuffer, ou seja, quantos bytes serão enviados.
       
            
        #finalmente vamos transmitir os todos. Para isso usamos a funçao sendData que é um método da camada enlace.
        #faça um print para avisar que a transmissão vai começar.
        #tente entender como o método send funciona!
        #Cuidado! Apenas trasmita arrays de bytes!

        n_random = random.randint(10,30)

        txBuffer = bytes([n_random])
        com1.sendData(np.asarray(txBuffer))
        print(f'numero de comandos: {n_random}')


        lista = randomizador(n_random)
        for i in lista:
            txBuffer = comandos[i]
            tamanho_tx_buffer = len(txBuffer)
            tamanho_tx_buffer_bytes = bytes([tamanho_tx_buffer])
            print(f'enviou o comando {i} com tamanho {np.asarray(tamanho_tx_buffer_bytes)} bytes')
            com1.sendData(np.asarray(txBuffer))

            time.sleep(1)
            com1.sendData(np.asarray(lista[i]))
            print("enviou o byte {}" .format(lista[i]))
            time.sleep(1)

        # com1.sendData(np.asarray(txBuffer))  #as array apenas como boa pratica para casos de ter uma outra forma de dados
          
        # A camada enlace possui uma camada inferior, TX possui um método para conhecermos o status da transmissão
        # O método não deve estar fincionando quando usado como abaixo. deve estar retornando zero. Tente entender como esse método funciona e faça-o funcionar.
        # txSize = com1.tx.getStatus()
        # print('enviou = {}' .format(txSize))
        
        #Agora vamos iniciar a recepção dos dados. Se algo chegou ao RX, deve estar automaticamente guardado
        #Observe o que faz a rotina dentro do thread RX
        #print um aviso de que a recepção vai começar.
        
        #Será que todos os bytes enviados estão realmente guardadas? Será que conseguimos verificar?
        #Veja o que faz a funcao do enlaceRX  getBufferLen
      
        #acesso aos bytes recebidos
        # txLen = len(txBuffer)
        # rxBuffer, nRx = com1.getData(txLen)
        # print("recebeu {} bytes" .format(len(rxBuffer)))
        
        # for i in range(len(rxBuffer)):
        #     print("recebeu {}" .format(rxBuffer[i]))


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
