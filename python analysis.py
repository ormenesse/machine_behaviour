from pymongo import MongoClient
from matplotlib import pyplot as plt
import csv
import os
import re
import numpy as np
# pprint library is used to make the output look more pretty
from pprint import pprint

#classe definindo dia básico de logs da máquina
class dia_evento:
	def __init__(self, data, dados, minutos):
		self.dia = data
		self.data = dados #array com 2 dimensoes - eventcode e horario
		self.min = minutos

def get_min(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 60 + int(m) * 1  #+ int(s)/60

def main():
	# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
	client = MongoClient("127.0.0.1")
	#db=client.admin
	db = client.MBA
	# Issue the serverStatus command and print the results
	#serverStatusResult=db.command("serverStatus")
	# pprint(serverStatusResult)
	# Lendo CSV's com log's necessários.
	lista_arquivos = os.listdir("/home/apt/Documents/mba")
	#pprint(lista_arquivos)
	p = re.compile("\S+")
	lista_dias = np.array([])
	for arquivos in lista_arquivos:
		if ".csv" in arquivos:
			with open("/home/apt/Documents/mba/"+arquivos) as csvfile:
				#a ideia original é fazermos uma relevancia de eventos por dia e tetantar encontrar alguma disparidade ou algum problema com isso. Se não der certo, tentamos com outra coisa.
				lendoarquivo = csv.reader(csvfile, delimiter=",", quotechar="|")
				dia = "01/01/0001"
				dados = np.array([])
				minutes = np.array([])
				for linha in lendoarquivo:
					#aqui eu comeco a processar csv's com logs
					if dia == p.match(linha[1]).group():
						#mesmo dia
						dados = np.append(dados, int(linha[3][1:len(linha[3])-1]))
						#pprint(linha[1][12:len(linha[1])-1])
						minutes = np.append(minutes, get_min(linha[1][12:len(linha[1])-1])) #17/11/2017 04:36:02
					else:
						lista_dias = np.append(lista_dias, dia_evento(dia, dados, minutes))
						dia = p.match(linha[1]).group()
						dados = np.array([])
						minutes = np.array([])
	#aqui já separei meus dados e posso começar a analisar os arquivos
	#pprint(lista_dias)
	pprint("Fim de configuração dos dos dados...")
	consolidados = np.matrix('')
	for dias in lista_dias:
		consolidados = np.append(consolidados, [dias.data, dias.min])
	#plotaremos um grafico para entendermos os dados.
	plt.scatter(consolidados, consolidados, color='green')
	plt.title("Eventos/minutos(dia)")
	plt.xlabel("minutos")
	plt.ylabel("eventos")
	plt.show()
	eventos = dados[ np.where( dados == 4688) ] # isso aqui funciona/preciso separar os eventos apenas.
	

main()