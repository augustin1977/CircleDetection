import tkinter as tk
import cv2
from PIL import Image, ImageTk
import time
import numpy as np
import ferramentas 
import device
import threading


# constantes do projeto
postexth=10
postextv=10
undersize=15
onsize=35
oversize=50
tresholder1=135
tresholder2=235
sensibilidade=45
parcial=1.3
alfa=1
beta=0
altura= 480
numero_medidas=5
delay=1 #  1 para webcam ou velocidade normal e outro valor para camera lenta em videos
class Circulos():
	def __init__(self):
		self.circulos=[]
		self.tresholder1=tresholder1
		self.tresholder2=tresholder2
		self.sensibilidade=sensibilidade
	def getCirculos(self):
		return self.circulos
			
	def atualizaCirculos(self, imagem,tresholder1,tresholder2,sensibilidade,hmi,smi,vmi,hma,sma,vma):
		self.tresholder1=tresholder1
		self.tresholder2=tresholder2
		self.sensibilidade=sensibilidade
		self.hmi=hmi
		self.smi=smi
		self.vmi=vmi
		self.hma=hma
		self.sma=sma
		self.vma=vma
		
		img = imagem.copy()
		# aplica filtros de suavização de ruidos	
		img=cv2.bilateralFilter(img,3,800,800)
		#img=cv2.blur(img,(2,2))
		
		# aplica hiltro de cor HSB
		
		lower = np.array([self.hmi, self.smi, self.vmi],dtype="uint8")
		upper = np.array([self.hma, self.sma, self.vma],dtype="uint8")
		#print(lower,upper)
		hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
		mask = cv2.inRange(hsv, lower, upper)
		img = cv2.bitwise_and(img,img,mask= mask)
			
		
		#Converte para cinza e aplica o canny
		img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		img=cv2.Canny(img,self.tresholder1,self.tresholder2)
		
		
		# dilata contornos
		#kernel = np.ones((1, 1))
		#img = cv2.dilate(img, kernel, iterations=2)
		
		# inverte a imagem
		img= cv2.bitwise_not(img)
		
		#finalmente encontra os circulos
		# paramentros definidos no codigo:
		# 		-distancia_minima=7(chute)
		#		-Fator de escala=0.9
		#		-raiominimo=5(chute)
		#		-raioMaximo=180(chute)

		self.circulos=[]
		for i in range(numero_medidas):
			c=cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,7,param1=self.tresholder2+self.tresholder1,param2=self.sensibilidade,minRadius=3,maxRadius=90)
			if (not type(c)==type(None)):
				for circulo in c:
					#print(circulos)
					self.circulos.append(circulo)
		
		
		#self.circulos = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,8,param1=self.tresholder2,param2=self.sensibilidade,minRadius=7,maxRadius=180) # linha antiga preservada para historico e para voltar versão
		#print(self.circulos) 
		#se não encontrar nenhum, ignora as rotinas de identficação de repetidos e a conversão para uint16
		if (not type(self.circulos)==type(None)):
			self.circulos=ferramentas.separa_circulos(self.circulos,parcial)
			#self.circulos = np.uint16(np.around(self.circulos)) 
	# somente faz a converão para RGBA
		return img
	
		
class Tela(object):
	# cria o construtor da tela
	def __init__(self,i):
		#cria o objeto circulos
		self.circulos=Circulos()
		self.circulos_encontrado=[]
		pasta=r"D:\Eric\Documentos\USP\Mestrado\RollerScreen\videos"
		#self.cap = cv2.VideoCapture('rtsp://192.168.0.27:10000/h264_pcm.sdp') # Camera IP
		#self.cap = cv2.VideoCapture('http://192.168.0.27:10000/video') # Camera IP
		#self.cap = cv2.VideoCapture(0) # webcam 1
		self.cap=cv2.VideoCapture(pasta+r'\DSC_4208.MOV') # video padrão
		#self.cap=cv2.VideoCapture(pasta+r'\VID_20210524_201735.mp4')#Video em 60fps
		_,self.frame=self.cap.read() # atualização webcam
		self.delay=delay
		largura = self.frame.shape[1]
		altura = self.frame.shape[0]
		proporcao = float(altura/largura)
		self.resolucao=(640,int(640*proporcao))
		# define variaveis de calculo do diametro do circulo
		self.a=alfa
		self.b=beta
		self.hmi=0
		self.smi=0
		self.vmi=0
		self.hma=255
		self.sma=255
		self.vma=255
		#define o titulo da tela
		i.title("Identificador de Pelota V 1.0")
		# define o tamanho
		#i.geometry("1280x600+100+100")
		i.resizable(False,False)
		i.iconbitmap("icon.ico")
		# Cria variaveis tresholder
		self.tresholder1=tresholder1
		self.tresholder2=tresholder2
		self.sensibilidade=sensibilidade
		#cria frames para organizar a tela e empacota 
		# frame tela para a tela em duas partes uma sobre a outra
		# frame contoles para os controles
		# frame Frame_imagens para as imagens lado a lado 
		# 5 frames para sendo:
		# frame1 para imagem colorida 
		# frame2 para imagem vetorizada
		# frame3 para controles threshold1
		# frame4 para controles threshold2
		# frame5 para para criar um espaço entre os thresholds
		# frame6 para espaço para o controle de Sensibilidade
		# frame7 pas sensibilidade
		# frame8 para espaço para campos de ajuste de tamanho
		# frame9 para ajustes de tamanho
		# frame 10 para controle de cor maxima
		# frame 11 para controle cor minima
		# frame 12 botos para controle fluxo video
		
		self.frameTela=tk.Frame(i)
		self.controles= tk.Frame(self.frameTela)
		self.Frame_imagens=tk.Frame(self.frameTela)
		self.frame1=tk.Frame(self.Frame_imagens)
		self.frame2=tk.Frame(self.Frame_imagens)
		self.frame3=tk.Frame(self.controles)
		self.frame4=tk.Frame(self.controles)
		self.frame5=tk.Frame(self.controles)
		self.frame6=tk.Frame(self.controles)
		self.frame7=tk.Frame(self.controles)
		self.frame8=tk.Frame(self.controles)
		self.frame9=tk.Frame(self.controles)
		self.frame10=tk.Frame(self.controles)
		self.frame11=tk.Frame(self.controles)
		self.frame12=tk.Frame(self.controles)
		
		
		
		# empacota todos os frames na ordem de disposição na tela
		self.frameTela.pack()
		self.Frame_imagens.pack()
		self.controles.pack()
		self.frame1.pack(side=tk.LEFT)
		self.frame2.pack(side=tk.LEFT)
		self.frame3.pack(side=tk.LEFT)
		self.frame5.pack(side=tk.LEFT)
		self.frame4.pack(side=tk.LEFT)
		self.frame6.pack(side=tk.LEFT)
		self.frame7.pack(side=tk.LEFT)
		self.frame8.pack(side=tk.LEFT)
		self.frame9.pack(side=tk.LEFT)
		self.frame10.pack(side=tk.LEFT)
		self.frame11.pack(side=tk.LEFT)
		self.frame12.pack(side=tk.LEFT)
		
		# Labels para tresholder e botões para incremetar e decrementar
		nome1= tk.Label(self.frame3,text="Treshold 1")
		nome2= tk.Label(self.frame4,text="Treshold 2")
		nome3= tk.Label(self.frame7,text="Sensibilidade")
		nome4= tk.Label(self.frame9,text="Alfa e Beta")
		nome5 = tk.Label(self.frame10,text="HSb Min")
		nome6 = tk.Label(self.frame11,text="HSb Max")
		espaco1=tk.Label(self.frame5,text="   ")
		espaco2=tk.Label(self.frame6,text="   ")
		espaco3=tk.Label(self.frame8,text="   ")
		self.slide1 = tk.Scale(self.frame3,from_=1, to=400, orient = tk.HORIZONTAL, command=self.Ajusta_contornos)
		self.slide1.set(self.tresholder1)
		self.slide2 = tk.Scale(self.frame4,from_=1, to=400, orient = tk.HORIZONTAL, command=self.Ajusta_contornos)
		self.slide2.set(self.tresholder2)
		self.slide3 = tk.Scale(self.frame7,from_=1, to=59, orient = tk.HORIZONTAL, command=self.Ajusta_contornos)
		self.slide3.set(self.sensibilidade)
		
		
		#define as entradas da transformação linear para ajuste de pixel para mm
		self.alfa=tk.Entry(self.frame9)
		self.beta=tk.Entry(self.frame9)
		self.alfa=ferramentas.set_text(str(self.a),self.alfa)
		self.beta=ferramentas.set_text(str(self.b),self.beta)
		
		# define variaves H,S,V max e min
		self.hmin=tk.Entry(self.frame10)
		self.smin=tk.Entry(self.frame10)
		self.vmin=tk.Entry(self.frame10)
		
		self.hmin=ferramentas.set_text(str(self.hmi),self.hmin)
		self.smin=ferramentas.set_text(str(self.smi),self.smin)
		self.vmin=ferramentas.set_text(str(self.vmi),self.vmin)
		
		self.hmax=tk.Entry(self.frame11)
		self.smax=tk.Entry(self.frame11)
		self.vmax=tk.Entry(self.frame11)
		
		self.hmax=ferramentas.set_text(str(self.hma),self.hmax)
		self.smax=ferramentas.set_text(str(self.sma),self.smax)
		self.vmax=ferramentas.set_text(str(self.vma),self.vmax)
		
		self.alfa=ferramentas.set_text(str(self.a),self.alfa)
		self.beta=ferramentas.set_text(str(self.b),self.beta)
		
		ajusta=tk.Button(self.frame9, text="ajusta",command=self.define_alfa_beta)


		slow1=tk.Button(self.frame12,text="Normal slow", command=self.setdelay1)
		slow2=tk.Button(self.frame12,text="Super slow ", command=self.setdelay2)
		
		# somente define os posicionamentos dos controles na tela
		nome1.pack()
		self.slide1.pack(side=tk.LEFT)
		nome2.pack()
		self.slide2.pack(side=tk.LEFT)
		nome3.pack()
		self.slide3.pack(side=tk.LEFT)
		nome4.pack()
		nome5.pack()
		nome6.pack()
		self.alfa.pack(side=tk.LEFT)
		self.beta.pack(side=tk.LEFT)
		self.hmin.pack()
		self.smin.pack()
		self.vmin.pack()
		
		self.hmax.pack()
		self.smax.pack()
		self.vmax.pack()
		
		
		ajusta.pack(side=tk.LEFT)
		espaco1.pack()
		espaco2.pack()
		espaco3.pack()
		
		slow1.pack()
		slow2.pack()
	
	
		
		# Cria um espaço para o video e empacota
		self.logo1=tk.Label(self.frame1)
		self.logo2=tk.Label(self.frame2)
		self.tempo=1
		self.t=threading.Thread(target=self.show_image)
		#self.show_image()
		self.t.start()
	
	def setdelay1(self):
		if self.delay==250:
			self.delay=1
		else:
			self.delay=250
	def setdelay2(self):
		if self.delay==1000:
			self.delay=1
		else:
			self.delay=1000	
			
	def define_alfa_beta(self):
		# copia os valores de alfa e beta do campos do formulario para as variaveis de conversão das transormação linear
		self.a=float(self.alfa.get())
		self.b=float(self.beta.get())
		#Busca valores do HSB
		self.hmi=float(self.hmin.get())
		self.smi=float(self.smin.get())
		self.vmi=float(self.vmin.get())
		self.hma=float(self.hmax.get())
		self.sma=float(self.smax.get())
		self.vma=float(self.vmax.get())
		
		
		
	def preparaimagem(self,imagem, vetoriza):
		# trata a imagem recebida, gera o vetor de circulos encontrados e retorna a imagem tratada e a original prontas para serem exibidas 
		if (vetoriza):
			img = self.circulos.atualizaCirculos(imagem,self.tresholder1,self.tresholder2,self.sensibilidade,self.hmi,self.smi,self.vmi,self.hma,self.sma,self.vma)
			self.circulos_encontrado=self.circulos.getCirculos()
		else:
			img=imagem.copy()
			img=cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
		img = Image.fromarray(img)
		img = ImageTk.PhotoImage(img)
		return img
	def buscaImagem(self,modo):
		#print(modo)
		self.frame= cv2.resize(self.frame,self.resolucao, interpolation = cv2.INTER_AREA)
		if (modo):
			
			self.logo1.image = self.preparaimagem(self.frame,True)
			#print(self.circulos_encontrado)
			# inserindo os circulos no frame
			
			#Inserindo informações de FPS na frame convertendo para RGB e empacotando		
			
			# prepara a imagem para ser exibida
			
		else:
			if (not type(self.circulos_encontrado)==type(None)):
				#print(self.circulos,"\n")
				contador=0
				for circulo in self.circulos_encontrado:
					print(circulo,contador)
					contador+=1
					c=ferramentas.ajusta_tamanho(circulo[2],self.a,self.b)
					#Classifica o tamanho
					if c<=undersize: 
						color=(0,0,255) # Vemelho
						
					elif c<=onsize:
						color=(0,255,0) # verde
						
					elif c<=oversize:
						color=(255,0,0) # Azul
						
					else:
						color=(0,255,255) # amarelo
						
					cv2.putText(self.frame,"{:1.1f}".format(c), (int(circulo[0])-postexth,int(circulo[1])+postextv+int(circulo[2])), 0, 0.4, (110,255,110))
					cv2.circle(self.frame,(int(circulo[0]),int(circulo[1])),int(circulo[2]),color,2)
			cv2.rectangle(self.frame,(15,30,50,30),(255,255,255),thickness=-1)
			cv2.putText(self.frame,("{:2.0f}".format(self.fps)), (20,50), 0, 0.5, (10,200,30))
			self.logo2.image = self.preparaimagem(self.frame,False)
			

	def show_image(self):
		# calculando fps
		self.fps= 1/(time.time()-self.tempo)
		self.tempo= time.time()
		
		# capiturando imagem da webcam
		_,self.frame=self.cap.read()
		#print(type(self.frame))
		if (type(self.frame)!=type(None)):			
			#t2=threading.Thread(target=self.buscaImagem, args=(True,))
			#t1=threading.Thread(target=self.buscaImagem, args=(False,))
			#t1.start()
			#t2.start()
			#t2.join()
			#t1.join()
			self.buscaImagem(True)
			self.buscaImagem(False)
			self.logo1.configure(image=self.logo1.image)
			self.logo2.configure(image=self.logo2.image)
			self.logo1.pack()
			self.logo2.pack()
			# faz a recursividade para atualização da imagem com 1 ms
			self.logo1.after(self.delay, self.show_image)
		else:
			print("----Erro ----\n Imagem não detectada ou fim de arquivo de video")	
		
		
	def Ajusta_contornos(self,pos):
		#rotina de controle dos ajustes da tela
		self.tresholder1=int(self.slide1.get())
		self.tresholder2=int(self.slide2.get())	
		self.sensibilidade=60-int(self.slide3.get())
	


t= tk.Tk()
Tela(t)
t.mainloop()
print("fim")
#cap.release()

cv2.destroyAllWindows()



