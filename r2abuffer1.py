"""
Universidade de Brasilia -  UnB
Redes de Computadores - Turma 3 - Professor Caetano 2023/2
Projeto ABR

Grupo 9

Integrantes
Lucas Silva Carneiro 21/1026655
Hudson Caua Costa Lima 21/1055512
Davy Viana Guimaraes 21/1055559

"""

from r2a.ir2a import IR2A
from player.parser import *
from base.whiteboard import *
import time
from base.timer import Timer


class R2ABuffer1(IR2A):
    def __init__(self, id):
        # DECLARACAO DE VALORES
        IR2A.__init__(self, id)
        self.qi = []  # Lista de qualidades de video disponiveis
        self.currentQuality = 0  # Qualidade de video atual
        self.bufferSize = 0  # Tamanho de buffer ocupado
        self.bufferMaxSize = 0  # Tamanho de buffer maximo
        self.timeLastRequest = 0  # Tempo da ultima request
        self.deltaTimeLastRequest = 0  # Diferenca entre o tempo de request e response
        self.lastChunkTime = 0  # Tempo de transmissao do ultimo chunk
        self.lastChunkSize = 0  # Tamanho do ultimo chunk
        self.transmissionRate = 0  # Taxa de transmissão do ultimo chunk
        self.chunkMap = []  # Mapa de chunks
        self.timer = Timer.get_instance()  # Tempo
        self.safetyNumber = 1  # Numero de seguranca para ajuste do algoritmo

    def handle_xml_request(self, msg):
        # Salva o tamanho maximo de buffer na variavel bufferMaxSize
        self.bufferMaxSize = Whiteboard.get_max_buffer_size(self.whiteboard)
        self.send_down(msg)

    def handle_xml_response(self, msg):
        # Salva a lista de qualidades disponiveis na lista qi
        parsed = parse_mpd(msg.get_payload())
        self.qi = parsed.get_qi()

        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        # Salva o tamanho de buffer na variavel Buffersize
        self.bufferSize = Whiteboard.get_amount_video_to_play(self.whiteboard)

        # Salva o tempo atual de execucao do codigo na variavel local currenttime
        currenttime = self.timer.get_current_time()

        # --- LOGICA PRINCIPAL ---

        #  Se o tamanho do buffer carregado for menor ou igual a 5
        if self.bufferSize <= 5:
            self.currentQuality = 0  # Qualidade de transmissao 0
            self.safetyNumber += 2.5  # Aumenta o safetyNumber para deixar o codigo mais conservador
        # Se o tamanho de buffer carregado for maior que 5
        else:
            # Loop inverso do chunkMap, comeca pelo ultimo valor do chunkMap
            for g in range(len(self.chunkMap) - 1):
                # Salva o indice inverso na variavel indice inverso
                indiceinverso = len(self.chunkMap) - g - 1
                # Se o tamanho de buffer carregado for maior que o safetyNumber * o tempo do chunkMap
                if self.bufferSize > self.safetyNumber * self.chunkMap[indiceinverso]:
                    # Se o indice do loop g for igual ao comprimento da lista chunkMap
                    if g == len(self.chunkMap) - 1:
                        # Qualidade de transmissao maxima
                        self.currentQuality = len(self.chunkMap) - 1
                        # Se o safetyNumber for maior ou igual a 4
                        if self.safetyNumber >= 4:
                            self.safetyNumber -= 3  # Diminui o safetyNumber em 3
                    # Se o indice do loop for menor que o comprimento da lista chunkMap
                    else:
                        # Se a porcentagem de buffer ocupado for <= que 10%
                        if self.bufferSize / self.bufferMaxSize <= 0.1:
                            self.safetyNumber += 2  # Aumenta safetyNumber em 2
                        # Se a porcentagem de buffer ocupado for <= que 20%
                        elif self.bufferSize / self.bufferMaxSize <= 0.2:
                            self.safetyNumber += 1  # Aumenta safetyNumber em 1
                        # Se a porcentagem de buffer ocupado for <= que 30%
                        elif self.bufferSize / self.bufferMaxSize <= 0.3:
                            self.safetyNumber += 0.5  # Aumenta safetyNumber em 0.5
                        # Se a porcentagem de buffer ocupado for <= que 40%
                        elif self.bufferSize / self.bufferMaxSize <= 0.4:
                            self.safetyNumber += 0.25  # Aumenta safetyNumber em 0.25
                        # Se a porcentagem de buffer ocupado for >= que 90%
                        elif self.bufferSize / self.bufferMaxSize >= 0.9:
                            # Se o safetyNumber for >= 4
                            if self.safetyNumber >= 4:
                                self.safetyNumber -= 3  # Diminui o safetyNumber em 3
                                # Se a qualidade atual for menor que a maxima
                                if self.currentQuality < len(self.qi) - 1:
                                    # Qualidade maxima
                                    self.currentQuality = len(self.qi) - 1
                        # Se a porcentagem de buffer ocupado for >= que 80%
                        elif self.bufferSize / self.bufferMaxSize >= 0.8:
                            # Se o safetyNumber for >= 3
                            if self.safetyNumber >= 3:
                                self.safetyNumber -= 2  # Diminui o safetyNumber em 2
                        # Se a porcentagem de buffer ocupado for >= que 70%
                        elif self.bufferSize / self.bufferMaxSize >= 0.7:
                            # Se o safetyNumber for >= 2
                            if self.safetyNumber >= 2:
                                self.safetyNumber -= 1  # Diminui o safetyNumber em 1
                        # Se a porcentagem de buffer ocupado for >= que 60%
                        elif self.bufferSize / self.bufferMaxSize >= 0.6:
                            # Se o safetyNumber for >= 1.25
                            if self.safetyNumber >= 1.25:
                                self.safetyNumber -= 0.50  # Diminui o safetyNumber em 0.5
                        # Se a porcentagem de buffer ocupado for >= que 50%
                        elif self.bufferSize / self.bufferMaxSize >= 0.5:
                            # Se o safetyNumber for >= 1
                            if self.safetyNumber >= 1:
                                self.safetyNumber -= 0.25  # Diminui o safetyNumber em 0.25
                        self.currentQuality = indiceinverso
                        break

        # Adiciona qualidade salva na variavel currentQuality para request
        msg.add_quality_id(self.qi[self.currentQuality])

        # Salva o tempo atual como tempo de ultimo request
        self.timeLastRequest = time.perf_counter()

        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        # Salva o tempo de download do ultimo chunk na variavel lastChunktime
        self.lastChunkTime = time.perf_counter() - self.timeLastRequest

        # Salva a diferenca de tempo entre o tempo do ultimo request e response na variavel deltaTimeLastRequest
        self.deltaTimeLastRequest = time.perf_counter() - self.timeLastRequest

        # Salva o tamanho do ultimo chunk e salva na variavel lastChunkSize
        self.lastChunkSize = msg.get_bit_length()

        # --- CHUNKMAP ---
        # Se o tamanho do ultimo chunk for maior que 0
        if self.lastChunkSize > 0:
            # Salva a taxa de transmissao do ultimo chunk na variavel transmissionRate
            self.transmissionRate = float(self.lastChunkSize) / self.deltaTimeLastRequest

            # Esvazia a lista chunkMap
            self.chunkMap.clear()

            # Loop do comprimento da lista de qualidades
            for t in range(len(self.qi)):
                # Se o indice t for 0
                if t == 0:
                    # Adiciona o tempo de download do ultimo chunk ao chunkMap na posicao 0
                    self.chunkMap.append(self.deltaTimeLastRequest)
                # Se o indice t for menor que o comprimento da lista de qualidades e diferente do tamanho maximo
                elif t < len(self.qi) and t != len(self.qi) - 1:
                    # Adiciona a proporcao de tempo necessario para realizar download de cada qualidade na lista
                    # utilizando a taxa de transmissao do ultimo chunk como parametro
                    self.chunkMap.append((self.qi[t+1] * self.chunkMap[t-1]) / self.qi[t])
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass
