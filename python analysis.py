from pymongo import MongoClient
from matplotlib import pyplot as plt
import sys
import csv
import os
import re
import numpy as np
# pprint library is used to make the output look more pretty
from pprint import pprint
import pickle # serializacao de objetos
from sklearn import svm
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from scipy import stats
from sklearn.preprocessing import StandardScaler

#classe definindo dia básico de logs da máquina
class dia_evento:
  def __init__(self, data, dados, minutos):
    self.dia = data
    self.data = dados #array com 2 dimensoes - eventcode e horario
    self.min = minutos

class evento:
  def __init__(self, evnt, minutos):
    self.evento = evnt
    self.min = np.array(minutos)
  #a ideia é serparar por classes o time de evento de cada eventid.
  def update_time_array(self, min_add):
    self.min = np.append(self.min, min_add)


def get_min(time_str):
    h, m, s = time_str.split(':')
    minuto = int(h) * 60 + int(m) * 1  #+ int(s)/60
    return minuto

def save_to_file(objeto, nome_arquivo):
  with open(nome_arquivo, 'wb') as output:
    pickle.dump(objeto, output, pickle.HIGHEST_PROTOCOL)

def load_file(nome_arquivo):
  with open(nome_arquivo, 'rb') as input:
    objeto = pickle.load(input)
  return objeto


def get_eventos():
  # connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
  client = MongoClient("127.0.0.1")
  #db=client.admin
  db = client.MBA
  # Issue the serverStatus command and print the results
  #serverStatusResult=db.command("serverStatus")
  # pprint(serverStatusResult)
  # Lendo CSV's com log's necessários.
  lista_arquivos = os.listdir("./mba")
  #pprint(lista_arquivos)
  p = re.compile("\S+")
  lista_dias = np.array([])
  eventos = np.array([])
  for arquivos in lista_arquivos:
    if ".csv" in arquivos:
      with open("./mba/"+arquivos) as csvfile:
        #a ideia original é fazermos uma relevancia de eventos por dia e tetantar encontrar alguma disparidade ou algum problema com isso. Se não der certo, tentamos com outra coisa.
        lendoarquivo = csv.reader(csvfile, delimiter=",", quotechar="|")
        dia = "01/01/0001"
        dados = np.array([])
        minutes = np.array([])
        for index, linha in enumerate(lendoarquivo):
          if index != 0:
            #aqui eu comeco a processar csv's com logs
            tem_evnt = False #tratamento para criacao de arrays
            if dia == p.match(linha[1]).group():
              #mesmo dia
              dados = np.append(dados, int(linha[3][1:len(linha[3])-1]))
              #pprint(linha[1][12:len(linha[1])-1])
              minutes = np.append(minutes, get_min(linha[1][12:len(linha[1])-1])) #17/11/2017 04:36:02
              #separando por evento também para que se gere outra inteligencia
              tem_evnt = False
              for idx,evnt in enumerate(eventos):
                try:
                  #checando para ver se o evento existe
                  #pprint("Esse é igual " + str(eventos[idx].evento) +" a esse" + str(int(linha[3][1:len(linha[3])-1]))
                  if eventos[idx].evento == int(linha[3][1:len(linha[3])-1]):
                    if int(linha[3][1:len(linha[3])-1]) == 4624 and "Tipo de logon: 5" in linha[4]:
                      #não há muito o que fazer, não quero esses eventos
                      #implementar novas ideias aqui
                      pass
                    else:
                      minuto = get_min(linha[1][12:len(linha[1])-1])
                      #pprint(minuto)
                      evnt.update_time_array(minuto)
                      tem_evnt = True
                except:
                  pprint("Erro ao criar classes de eventos")
                  pass #sem tempo para analisar isso agora  
              if tem_evnt == False:
                if int(linha[3][1:len(linha[3])-1]) == 4624 and "Tipo de logon: 5" in linha[4]:
                  #não há muito o que fazer, não quero esses eventos
                  #implementar novas ideias aqui
                  pass
                else:
                  eventos = np.append(eventos, evento(int(linha[3][1:len(linha[3])-1]), get_min(linha[1][12:len(linha[1])-1])))
            else:
              # lista de dias tudo junto
              lista_dias = np.append(lista_dias, dia_evento(dia, dados, minutes))
              dia = p.match(linha[1]).group()
              dados = np.array([int(linha[3][1:len(linha[3])-1])])
              minutes = np.array([get_min(linha[1][12:len(linha[1])-1])])
              # lista por eventos separado
              for idx,evnt in enumerate(eventos):
                try:
                  if evnt.evento == int(linha[3][1:len(linha[3])-1]):
                    if int(linha[3][1:len(linha[3])-1]) == 4624 and "Tipo de logon: 5" in linha[4]:
                      #não há muito o que fazer, não quero esses eventos
                      #implementar novas ideias aqui
                      pass
                    else:
                      minuto = get_min(linha[1][12:len(linha[1])-1])
                      evnt.update_time_array(minuto)
                      tem_evnt = True
                except:
                  pass #método a ser implementado
              if tem_evnt == False:
                if int(linha[3][1:len(linha[3])-1]) == 4624 and "Tipo de logon: 5" in linha[4]:
                  #não há muito o que fazer, não quero esses eventos
                  #implementar novas ideias aqui
                  pass
                else:
                  eventos = np.append(eventos, evento(int(linha[3][1:len(linha[3])-1]), get_min(linha[1][12:len(linha[1])-1])))
          else:
            pass
  #aqui já separei meus dados e posso começar a analisar os arquivos
  #pprint(lista_dias)
  pprint("Fim de configuração dos dos dados...")
  #consolidados = np.matrix('')
  consolidados = np.empty([2,1], dtype=int)
  #quero poder ver todos os eventos junto para facilidade de visualização
  for dias in lista_dias:
      #Aqui temos todos os eventos Windows Consolidados em só gráfico.
      consolidados = np.concatenate((consolidados, np.matrix([dias.data, dias.min])), axis=1)
  #plotaremos um grafico para entendermos os dados.S
  #pprint(consolidados[0, 1:])#teste para saber se array está funcionando
  plt.scatter(np.array(consolidados[1 , 1:]), np.array(consolidados[0 , 1:]), color='green')
  plt.title("Eventos/minutos(dia)")
  plt.xlabel("minutos")
  plt.ylabel("eventos")
  #olhando para apenas um evento, exemplo 4624
  pprint("Eventos detectados neste computador:")
  for evnt in enumerate(eventos):
    try:
      print("-> %d" % evnt.evento)
      #plt.scatter(evnt.min, evnt.evento)
    except:
      pass
  #plt.show() #cansei de ver o plot
  save_to_file(eventos, "eventos.pkl") #salvando todos eventos consolidados
  return eventos

def cria_modelos(eventos):
	print("Criando modelos de Outliers")

if __name__ == "__main__":
  eventos = get_eventos()
  cria_modelos(eventos)
