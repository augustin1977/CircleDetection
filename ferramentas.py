
def distancia(x1,y1,x2,y2):
	try:
		dx=(x1-x2)
		dy=(y1-y2)
		quad=dx*dx+dy*dy
		diag=quad**0.5
	except:
		diag=0
	return diag
	
def set_text(texto,campo):
		campo.delete(0,len(campo.get()))
		campo.insert(0,texto)
		return campo
			
def ajusta_tamanho(tamanho,a,b):
		# faz a transformação linerar de pixels para mm conforme ajuste de calibração
		tamanho = tamanho*a+b
		return tamanho

def separa_circulos(circulos,parcial):
		# rotina de identificação de reconhecimentos repetidos
		vetor=[]
		#print("circulos recebidos",circulos)
		#varre todos os circulos reconhecidos
		if (circulos!=[]):
			for circulo in circulos[0]:
				repetido=False
				cont=0
				media= True
				if media==True:
					#se eles ja estiverem no vetor e a distancia entre centros for menor que o raio vezes a variavel parcial então calcula a media da posição
					# caso contrario adiciona no vetor
					for item in vetor:
						d=distancia(circulo[0],circulo[1],item[0],item[1])
						if (d<((circulo[2]+item[2])/2)*parcial):
							repetido=True
							marca=cont
						cont+=1
					# calculo da media da posição de do raio
					if repetido:
						vetor[marca][0]=circulo[0]+vetor[marca][0]*vetor[marca][3]#coordenada x
						vetor[marca][1]=circulo[1]+vetor[marca][1]*vetor[marca][3]#coordenada y
						vetor[marca][2]=circulo[2]+vetor[marca][2]*vetor[marca][3]#raio da circufenrencia
						vetor[marca][3]+=1 # numero de circulos encontrados
						vetor[marca][0]=round(vetor[marca][0]/vetor[marca][3],2)
						vetor[marca][1]=round(vetor[marca][1]/vetor[marca][3],2)
						vetor[marca][2]=round(vetor[marca][2]/vetor[marca][3],2)
					else:
						vetor.append([circulo[0],circulo[1],circulo[2],1])		
				
				else:
					#se eles ja estiverem no vetor e a distancia entre centros for menor que o raio vezes a variavel parcial então pega a posição do maior
					# caso contrario adiciona no vetor
					for item in vetor:
						d=distancia(circulo[0],circulo[1],item[0],item[1])
						if (d<circulo[2]*parcial):
							repetido=True
							marca=cont
						cont+=1
					# calculo da media da posição de do raio
					if repetido:
						vetor[marca][0]=circulo[0]#coordenada x
						vetor[marca][1]=circulo[1]#coordenada y
						vetor[marca][2]=circulo[2]#raio da circufenrencia
						vetor[marca][3]+=1 # numero de circulos encontrados
					else:
						vetor.append([circulo[0],circulo[1],circulo[2],1])
			# faz um copia do vetor e grava no self.circulos				
			circulos=vetor.copy()
		
		return circulos
