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

        # Salva o safetyNumber na variavel local
        sftnumber = self.safetyNumber
        # Se o tamanho do buffer carregado for igual a 0
        if self.bufferSize == 0:
            self.currentQuality = 0  # Qualidade de transmissao 0
            self.safetyNumber += 2.5  # Aumenta o safetyNumber para deixar o codigo mais conservador
        # Se o tamanho de buffer carregado for maior que 0
        else:
            # Salva o tamanho do chunkMap - 1 numa variavel local
            chkmapsize = len(self.chunkMap) - 1
            # Loop inverso do chunkMap, comeca pelo ultimo valor do chunkMap
            for g in range(chkmapsize):
                # Salva o indice inverso na variavel indice inverso
                indiceinverso = chkmapsize - g
                # Se o tamanho de buffer carregado for maior que o safetyNumber * o tempo do chunkMap
                if self.bufferSize > self.chunkMap[indiceinverso]:
                    # Salva a taxa de buffer ocupado na variavel local bufferrate
                    bufferrate = self.bufferSize / self.bufferMaxSize
                    # Se a porcentagem de buffer ocupado for <= que 10%
                    if bufferrate <= 0.1:
                        # Se o safety number + 0.25 <= 50
                        if sftnumber + 2 <= 50:
                            self.safetyNumber += 2  # Aumenta safetyNumber em 2
                        # Se a porcentagem de buffer ocupado for <= que 20%
                        elif bufferrate <= 0.2:
                            # Se o safety number + 1 <= 50
                            if sftnumber + 1 <= 50:
                                self.safetyNumber += 1  # Aumenta safetyNumber em 1
                        # Se a porcentagem de buffer ocupado for <= que 30%
                        elif bufferrate <= 0.3:
                            # Se o safety number + 0.5 <= 50
                            if sftnumber + 0.5 <= 50:
                                self.safetyNumber += 0.5  # Aumenta safetyNumber em 0.5
                        # Se a porcentagem de buffer ocupado for <= que 40%
                        elif bufferrate <= 0.4:
                            # Se o safety number + 0.25 <= 50
                            if sftnumber + 0.25 <= 50:
                                self.safetyNumber += 0.25  # Aumenta safetyNumber em 0.25
                        # Se a porcentagem de buffer ocupado for >= que 90%
                        elif bufferrate >= 0.9:
                            # Se o safetyNumber - 3 for >= 2
                            if sftnumber - 3 >= 2:
                                self.safetyNumber -= 3  # Diminui o safetyNumber em 3
                        # Se a porcentagem de buffer ocupado for >= que 80%
                        elif bufferrate >= 0.8:
                            # Se o safetyNumber - 2 for >= 2
                            if sftnumber - 2 >= 2:
                                self.safetyNumber -= 2  # Diminui o safetyNumber em 2
                                self.currentQuality = indiceinverso
                                break
                        # Se a porcentagem de buffer ocupado for >= que 70%
                        elif bufferrate >= 0.7:
                            # Se o safetyNumber - 1 for >= que 2
                            if sftnumber - 1 >= 2:
                                self.safetyNumber -= 1  # Diminui o safetyNumber em 1
                                self.currentQuality = indiceinverso
                                break
                        # Se a porcentagem de buffer ocupado for >= que 60%
                        elif bufferrate >= 0.6:
                            # Se o safetyNumber - 0.50 for >= que 2
                            if sftnumber - 0.5 >= 2:
                                self.safetyNumber -= 0.50  # Diminui o safetyNumber em 0.5
                                self.currentQuality = indiceinverso
                                break
                        # Se a porcentagem de buffer ocupado for >= que 50%
                        elif bufferrate >= 0.5:
                            # Se o safetyNumber - 0.25 for >= que 2
                            if sftnumber - 0.25 >= 2:
                                self.safetyNumber -= 0.25  # Diminui o safetyNumber em 0.25
                                self.currentQuality = indiceinverso
                                break
                        self.currentQuality = indiceinverso
                        break

        # Informacoes uteis
        # print("SafetyNumber = ", self.safetyNumber)
        # print("ChunkMap = ", self.chunkMap)
        # print("LastChunkTime = ", self.lastChunkTime)
        # print("LastChunkSize = ", self.lastChunkSize)

        # Adiciona qualidade salva na variavel currentQuality para request
        msg.add_quality_id(self.qi[self.currentQuality])

        # Salva o tempo atual como tempo de ultimo request
        self.timeLastRequest = time.perf_counter()

        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        # Salva o tempo de download do ultimo chunk na variavel lastChunktime
        self.lastChunkTime = time.perf_counter() - self.timeLastRequest

        # Salva o tamanho do ultimo chunk e salva na variavel lastChunkSize
        self.lastChunkSize = msg.get_bit_length()

        # --- CHUNKMAP ---
        # Se o tamanho do ultimo chunk for maior que 0
        if self.lastChunkSize > 0:
            # Salva a taxa de transmissao do ultimo chunk na variavel transmissionRate
            self.transmissionRate = float(self.lastChunkSize) / self.lastChunkTime

            # Esvazia a lista chunkMap
            self.chunkMap.clear()

            # Salva o safetyNumber numa variavel local
            sftnumber = self.safetyNumber

            # Loop do comprimento da lista de qualidades
            for t in range(len(self.qi)):
                # Se o indice t for 0
                if t == 0:
                    # Adiciona o tempo de download do ultimo chunk multiplicado pelo safetyNumber
                    # ao chunkMap na posicao 0
                    self.chunkMap.append(self.lastChunkTime * sftnumber)
                # Se o indice t for menor que o comprimento da lista de qualidades e diferente do tamanho maximo
                elif t < len(self.qi) and t != len(self.qi) - 1:
                    # Formula (Qt+1) * (Tt-1) / Qt    Q = qualidade T = Tempo no chunkmap t = indice
                    # Adiciona ao chunkMap o tempo para baixar o chunk de uma qualidade abaixo
                    # multiplicado pela qualidade do proximo chunk divido pela qualidade do chunk t.
                    self.chunkMap.append((self.qi[t+1] * self.chunkMap[t-1]) / self.qi[t])
                # Se o indice t for igual ao comprimento da lista de qualidades
                else:
                    # Adiciona ao ChunkMap o tempo necessario para baixar o chunk de maior qualidade
                    # multiplicado pelo tempo necessario para baixar o chunk uma qualidade abaixo
                    # dividido pela qualidade abaixo
                    self.chunkMap.append((self.qi[t]) * self.chunkMap[t-1] / self.qi[t-1])

        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass