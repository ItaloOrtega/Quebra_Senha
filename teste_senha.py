from tkinter import *
from numba import cuda
import random
import numpy as np
import time
import matplotlib.pyplot as plt
import string

# criação da classe para guardar os dados da execução
class Execucao: #Classe do tabuleiro
  def __init__(self,type,cod, time):
    self.tipo = type
    self.vlr = cod
    self.tempo = time

#Criação da tupla de valores validos para as senhas
disc = list(string.ascii_lowercase) #Todos as letras minusculas
aux = list(string.ascii_uppercase) #Todos as letras maiusculas
disc = disc + aux
aux = []
for x in range(10):
  aux.append(str(x)) #Valores de 0 a 9
disc = disc + aux
aux = ['@','!','$','#','%','&','(',')','/','_','*','-','+',',','.','?']
disc = disc + aux
disc = tuple(disc)

execs = [] #Lista de todas as execuções ja feitas pela aplicação
try: #Tenta ler o arquivo de pontuação do usuário
  f = open("execucoes.bat", "r")
  for linha in f: #For para ler linha por linha o arquivo
    tipo = str(linha)
    tipo = tipo[0:len(tipo)-1]
    senha = str(next(f))
    senha = senha[0:len(senha)-1]#Necessario o -1 para não ler o \n do final da linha
    tempo = float(next(f))
    execucao = Execucao(tipo,senha,tempo)#Apos ter todos os dados é adicionado na lista a execução
    execs.append(execucao)
  f.close() #Fecha o arquivo
except: #Não possuindo o arquivo é passado
  pass


def graf(): #Função que mostra graficamente a media dos tempos de execução da GPU e da CPU para senhas de X tamanho
  maxx = 0 #Tamanho máximo de senhas feitas
  for x in execs: #For para descobrir a maior senha
    if len(x.vlr) > maxx:
      maxx = len(x.vlr)
  #Listas que possuem a somatoria dos tempos em cada tam. de senha e a qtd de vezes de cada uma
  aux1 = []
  cont1 = []
  aux2 = []
  cont2 = []
  for x in range(maxx): #Cria as listas do tamanho igual ao tamanho maximo de senha descoberta
    aux1.append(0)
    aux2.append(0)
    cont1.append(0)
    cont2.append(0)
  for x in execs: #Aloca todos os valores das execuções nas posições corretas
    if x.tipo == "CPU":
      aux1[len(x.vlr)-1] += x.tempo
      cont1[len(x.vlr)-1] += 1
    else:
      aux2[len(x.vlr)-1] += x.tempo
      cont2[len(x.vlr)-1] += 1
  #É feita a media de cada lista
  for x,y in enumerate(aux1): #Media do CPU
    if y != 0:
      y = y/cont1[x]
    else:
      y = 0
  
  for x,y in enumerate(aux2): #Media do GPU
    if y != 0:
      y = y/cont2[x]
    else:
      y = 0

  barWidth = 0.25 #Tamanho da barra de cada grafico
  fig = plt.subplots(figsize =(12, 8)) #Cria o grafico em si
  
  plt.title("Média de tempo gasto para\ndescobrir senhas", fontweight='bold') #Coloca o titulo
  br1 = np.arange(len(aux1)) #Aloca as posições do eixo X para cada lista
  br2 = [x + barWidth for x in br1]  
  #São criados os graficos em barras
  plt.bar(br1, aux1, color ='r', width = barWidth,
        edgecolor ='grey', label ='CPU')
  plt.bar(br2, aux2, color ='g', width = barWidth,
        edgecolor ='grey', label ='GPU')
  #Legendas para o eixo X e Y
  plt.xlabel('Tamanho da Senha em Caracteres', fontweight ='bold', fontsize = 15)
  plt.ylabel('Média de Segundos Gastos', fontweight ='bold', fontsize = 15)
  #Valores que separam os graficos, que é o tamanho das senhas
  plt.xticks([r + barWidth for r in range(len(aux2))],
        [r for r in range(1,maxx+1)])
  
  for i, v in enumerate(aux2): #Coloca os valores de cada barra no grafico
    linha = str(v)
    linha = linha[0:len(linha)-12]
    plt.text(i+0.15, v + 10, linha, color='g', fontweight ='bold')

  for i, v in enumerate(aux1): #Coloca os valores de cada barra no grafico
    linha = str(v)
    linha = linha[0:len(linha)-12]
    if i > 1:
      plt.text(i-0.15, v + 10, linha, color='r', fontweight ='bold')
    else:
      plt.text(i-0.25, v + 10, linha, color='r', fontweight ='bold')
  
  plt.legend() #Mostra a legenda
  plt.show() #Mostra o gráfico


def gerar(lbl): #Função que gera senhas aleatoriamente
  tam = random.randint(2, 10) #Escolhe o tamanho aleatorio das senhas, indo de 2 a 10
  linha = ""
  lbl.delete(0, 'end') #Limpa o que esta dentro da entrada
  for x in range(tam): #Gera aleatoriamente uma senha nova
    linha = linha+str(disc[random.randint(0, len(disc))])
  lbl.insert(END,linha) #Coloca o valor na entrada


def desc_gpu(entry, lbl): #Função para preparar/receber dados para a execução na GPU
  global execs
  linha = entry.get() #Recebe o texto na entrada
  if linha != "": #Sendo diferente de Vazio
    tamanho = [len(linha)] #Recebe o tamanho total da senha
    vlrs = [] #Lista da posições de cada caracter da senha
    resu = [-1] #Variavel que ira dizer em qual posição se encontra o valor da senha
    aux = [] #Lista para verificar se o thread atual é o valido para a senha
    for _,y in enumerate(linha):
      for i,j in enumerate(disc):
        if y == j:
          vlrs.append(i) #Aloca a posição na lista
          aux.append(0) #Aloca o valor 0
          break
    tam_total = [int(len(disc)),int(len(disc)**tamanho[0])] #Variavel que possui a qtd de caracteres possiveis numa senha e...
    #a qtd de possibilidades de senha desse tamanho
    start = time.time() #Começa a contagem de tempo de execução
    #Passa todas as variaveis para a GPU
    array = cuda.to_device(aux)
    senha = cuda.to_device(vlrs)
    resp = cuda.to_device(resu)
    alf = cuda.to_device(tam_total)
    tam = cuda.to_device(tamanho)
    add = [0] #Variavel que adiciona uma incrementação na posição atual do thread
    while resu[0] == -1:
      plus = cuda.to_device(add)
      descobre[1024**2, 1024](array,senha,resp,alf,tam,plus) #Executa a função utilizando 1024² blocos, com 1024 threads cada
      resu = resp.copy_to_host() #Copia o resultado para resu
      if resu[0] == -1: #Caso não tenha ainda encontrado a resposta
        add[0] += 1048576 #É adicionado 1024² a todos os threads para termos a posição correta
    tempo = time.time()-start #Para o tempo
    cont = len(linha)-1 #Contagem para o calculo da senha, onde é inicialmente igual à tamanho da senha - 1
    aux1 = resu[0] #Posição do thread que é valido
    final = "" #Resposta da senha
    for x in range(len(linha)): #For para percorrer cada posição da senha
      conta = int(aux1/(tam_total[0]**cont)) #Pega a posição atual e divide ela pela qtd de caracteres possiveis elevado a cont
      #Que resulta na posição inteira da letra
      final = final + str(disc[conta]) #Adiciona na senha descoberta esse caractere
      if cont != 0: #Caso cont seja diferente de 0...
        aux1 -= conta*(tam_total[0]**cont) #É subtraido da posição atual o resultado da conta, que é int, vezes a qtd de caracteres possiveis elevado a cont
        cont -= 1 #E diminui em 1 cont
    lbl.config(text=f"Pelo GPU a senha é: {final}\nFoi encontrada em {tempo} segundos") #Coloca na label a senha encontrada e o tempo que levou
    aux_ex = Execucao("GPU",final,tempo)
    execs.append(aux_ex) #Adiciona essa execução na lista de execuções


@cuda.jit
def descobre(array,senha,resp,alf,tam_senha,add): #Função que roda em cada thread da GPU
  i = cuda.grid(1) + add[0] #i é igual a posição atual do thread + add[0], que é a posição verdadeira do thread caso ja tenha sido feita +1 execução
  if i < alf[1]: #Caso i for menor que a quantidade total de possibilidades para esse tamanho de senha
    cont = tam_senha[0]-1 #Ocoorre a mesma coisa na formação da senha da func desc_gpu, mas com a alocação das posições no arr
    aux = cuda.grid(1) + add[0]
    flag = True #Flag para verificar se a posição atual é valida para a senha que estamos buscando
    for x in range(tam_senha[0]):
      conta = int(aux/(alf[0]**cont))
      array[x] = conta #O array recebe a posição que a letra se encontra na tupla
      if array[x] != senha[x]: #Caso o valor atual do array seja diferente de x, logo não é uma senha valida
        flag = False
        return
      if cont != 0:
        aux -= int(conta*(alf[0]**cont))
        cont -= 1
    if flag is True: #Caso a posição for a da senha que buscamos, resp recebe a posição
      resp[0] = cuda.grid(1)+ add[0]


def desc_cpu(entry, lbl): #Função para descobrir por meio da CPU a senha
  linha = entry.get()
  if linha != "": #Mesma coisa que ocorre no caso da gpu
    vlrs = []
    aux = []
    for _,y in enumerate(linha):
      for i,j in enumerate(disc):
        if y == j:
          vlrs.append(i)
          aux.append(0)
          break
    start = time.time()
    for x in range(len(disc)**len(linha)):
      cont = int(len(linha))-1
      arr = x
      flag = True
      for y in range(len(linha)):
        conta = int(arr/(int(len(disc))**cont))
        aux[y] = int(conta)
        if aux[y] != vlrs[y]: #Caso o valor seja diferente da senha, flag é falsa e sai desse loop
          flag = False
          break
        if cont != 0:
          arr -= int(conta*(len(disc)**cont))
          cont -= 1
      if flag is True: #Caso a Flag for true, logo a posição é a valida e saimos do loop principal
        break
    lbl.config(text=f"Pelo CPU a senha é: {linha}\nFoi encontrada em {time.time()-start} segundos")
    aux_ex = Execucao("CPU",linha,(time.time()-start))
    execs.append(aux_ex)


tela = Tk() #Tela principal
tela.configure(bg= "#CCCCCC")
tela.title("Quebra Senhas")
#Largura e altura da tela
larg = 420
alt = 330
#Calcula as dimensões da tela que esta sendo usado pelo usuario
larg_s = tela.winfo_screenwidth() # largura da tela do usuario
alt_s = tela.winfo_screenheight() # altura da tela do usuario
#calcaula as coordenadas para mostrar a tela da aplicação no meio do monitor
a = (larg_s/2) - (larg/2)
b = (alt_s/2) - (alt/2)
tela.geometry('%dx%d+%d+%d' % (larg, alt, a, b-50))
tela.resizable(False, False) #Desabilita a redimensão da janela

#Lbl_aux servem para dar um espaço das margens ou pular linhas, para melhor visualização da GUI
lbl_aux0 =  Label(tela, text="    ", bg= "#CCCCCC",font= "Calibri 10")
lbl_aux0.grid(row=0, column=0, columnspan=20)
lbl_aux1 =  Label(tela, text="    ", bg= "#CCCCCC",font= "Calibri 10")
lbl_aux1.grid(row=2, column=0, columnspan=20)
lbl_aux2 =  Label(tela, text="    ", bg= "#CCCCCC",font= "Calibri 10")
lbl_aux2.grid(row=3, column=0)
lbl_aux3 =  Label(tela, text="    ", bg= "#CCCCCC",font= "Calibri 10")
lbl_aux3.grid(row=4, column=0)
lbl_aux4 =  Label(tela, text="    ", bg= "#CCCCCC",font= "Calibri 10")
lbl_aux4.grid(row=6, column=0)
lbl_aux5 =  Label(tela, text="    ", bg= "#CCCCCC",font= "Calibri 10")
lbl_aux5.grid(row=8, column=0)


lbl_entrada = Label(tela, text="Digite/Gere sua senha:", bg= "#CCCCCC",font= "Calibri 10")
lbl_entrada.grid(row=1, column=1, columnspan=20)
#Entrada é onde a senha é gerada
entrada =  Entry(tela, text="",width=33, bg= "#FFFFFF", fg="#000000",font= "Calibri 10")
entrada.grid(row=2, column=1, columnspan=20)
#botão de gerar uma senha aleatoria
btt_gerar = Button(tela,text="Gerar", padx=10, pady=10, bg="#666666", fg="#FFFFFF", command=lambda:gerar(entrada))
btt_gerar.grid(row=3, column=1, columnspan=20)
#Botões para descobrir essa senha pelo CPU e GPU respectivamente
btt_desc_cpu = Button(tela,text="Descobrir pelo CPU", pady=10, bg="#666666", fg="#FFFFFF", command=lambda:desc_cpu(entrada, lbl_resposta))
btt_desc_cpu.grid(row=5, column=1)
btt_desc_gpu = Button(tela,text="Descobrir pelo GPU", pady=10, bg="#666666", fg="#FFFFFF", command=lambda:desc_gpu(entrada, lbl_resposta))
btt_desc_gpu.grid(row=5, column=3)
#Label onde mostra o resultado da execução do CPU/GPU
lbl_resposta = Label(tela, text="", bg= "#CCCCCC",font= "Calibri 10")
lbl_resposta.grid(row=7, column=1, columnspan=20)
#Botão para mostrar o grafico das execuções
btt_graf = Button(tela,text="Gráfico", pady=10, bg="#666666", fg="#FFFFFF", command=lambda:graf())
btt_graf.grid(row=9, column=2)
tela.mainloop() #Loop da tela

#Escreve no arquivo todas as execuções
f = open("execucoes.bat", "w")
for x,y in enumerate(execs):
  linha = str(y.tipo)
  f.write(linha+"\n")
  linha = str(y.vlr+"\n")
  f.write(linha)
  if x == len(execs)-1:
    linha = str(y.tempo)
  else:
    linha = str(y.tempo)+"\n"
  f.write(linha)
f.close()
