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


class R2ABuffer(IR2A):
    def __init__(self, id):
        # DECLARACAO DE VALORES
        IR2A.__init__(self, id)
        self.qi = []  # Lista de qualidades de video disponiveis
        self.currentQuality = 0  # Qualidade de video atual
        self.bufferSize = 0  # Tamanho de buffer ocupado
        self.timeLastRequest = 0  # Tempo da ultima request
        self.deltaTimeLastChunk = 0  # Diferenca entre o tempo de request e response
        self.bufferMap = []  # Mapa de tamanhos de buffer para mudanca de qualidade
        self.bufferReserve = 37  # Tamanho de reservatorio inicial
        self.bufferCushion = 17  # Tamanho de reservatorio de amortecimento
        self.bufferSuperior = 6  # Tamanho de reservatorio superior

    def handle_xml_request(self, msg):
        self.send_down(msg)

    def handle_xml_response(self, msg):
        # Salva a lista de qualidades disponiveis na lista qi
        parsed = parse_mpd(msg.get_payload())
        self.qi = parsed.get_qi()
        print(self.qi)

        # Criar Mapa de Buffer
        if len(self.qi) > 3:
            x = (len(self.qi) - 2) / len(self.qi)
            for i in range(1, (len(self.qi)-2)):
                self.bufferMap.append((37 + i * x))
        print(self.bufferMap)
        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        # Salva o tamanho de buffer na variavel Buffersize

        self.bufferSize = Whiteboard.get_amount_video_to_play(self.whiteboard)
        print("TAMANHO DE BUFFER DISPONIVEL = ", self.bufferSize)

        # --- LOGICA PRINCIPAL ---

        # Se o tamanho de buffer eh menor que o tamanho da reserva inicial
        if self.bufferSize <= self.bufferReserve:
            self.currentQuality = 0  # Qualidade de video 0
        # Se o tamanho de buffer for maior que reserva inicial e menor que tamanho superior
        elif self.bufferReserve < self.bufferSize < (self.bufferCushion + self.bufferReserve):
            if len(self.bufferMap) > 1:
                # Compara o tamanho de buffer com cada elemento do buffermap
                for i in range(len(self.bufferMap)):
                    if i < len(self.bufferMap):
                        if self.bufferSize < self.bufferMap[i]:
                            # Se o tamanho de buffer eh menor que o elemento i do bufferMap
                            self.currentQuality = i + 1  # Qualidade de video eh i + 1
                            break
                    else:
                        # Se o tamanho de buffer eh maior que todos os tamanhos no bufferMap
                        self.currentQuality = i + 1  # Qualidade de video i + 1
            else:
                self.currentQuality = 1
        # Se o tamanho de buffer for maior que reserva inicial e reserva de amortecimento
        else:
            self.currentQuality = len(self.qi) - 1  # Qualidade maxima
        print("QUALIDADE SELECIONADA = ", self.currentQuality)

        # Adiciona qualidade salva na variavel currentQuality para request
        msg.add_quality_id(self.qi[self.currentQuality])

        # Salva o tempo atual como tempo de ultimo request
        self.timeLastRequest = time.perf_counter()
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        print("DIFERENCA DE TEMPO DE REQUEST E RESPONSE = ", (time.perf_counter() - self.timeLastRequest))

        # Salva a diferenca de tempo entre o tempo do ultimo request e response na variavel deltaTimeLastChunk
        self.deltaTimeLastChunk = time.perf_counter() - self.timeLastRequest
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass
