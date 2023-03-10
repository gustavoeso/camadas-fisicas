from funcoes import *

img = 'G:\My Drive\Insper\Semestre 4\camadas-fisicas\Camadas\projeto 4\img\picara.jpg'
imgLida = open(img, 'rb').read()
lista_payload = monta_payload(imgLida)

monta_head1 = monta_head(1,len(lista_payload),0,0,0,0,0,0)
print(monta_head1)
print(monta_head1[1])