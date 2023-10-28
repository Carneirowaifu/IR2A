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

    def handle_xml_request(self, msg):
        self.send_down(msg)

    def handle_xml_response(self, msg):
        # Salva a lista de qualidades disponiveis na lista qi
        parsed = parse_mpd(msg.get_payload())
        self.qi = parsed.get_qi()
        print(self.qi)
        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        # Salva o tamanho de buffer na variavel Buffersize

        self.bufferSize = Whiteboard.get_amount_video_to_play(self.whiteboard)
        print("TAMANHO DE BUFFER DISPONIVEL = ", self.bufferSize)

        # --- LOGICA PRINCIPAL ---

        # Se o tamanho de buffer for maior que 8 segundos

        # Se o tempo entre request e response for menor que 4s e maior que 1s
        if 4 > self.deltaTimeLastChunk > 1 and self.bufferSize >= 8:
            if (self.currentQuality + 1) < len(self.qi):
                self.currentQuality += 1  # Aumenta qualidade em 1

        # Se 16 > tamanho do buffer >= 8 e o tempo entre request e response <= 1s
        elif 16 > self.bufferSize >= 8 and self.deltaTimeLastChunk <= 1:
            if (self.currentQuality + 2) < len(self.qi):
                self.currentQuality += 2  # Aumenta qualidade em 2

        # Se o tamanho do buffer >= 16 e o tempo entre request e response <= 1s
        elif self.bufferSize >= 16 and self.deltaTimeLastChunk <= 1:
            if (self.currentQuality + 3) < len(self.qi):
                self.currentQuality += 3  # Aumenta a qualidade em 3

        # Se o tempo entre request e response for menor que 5s e maior ou igual 4s
        elif (5 > self.deltaTimeLastChunk >= 4) and self.bufferSize > 8:
            if (self.currentQuality - 1) >= 0:
                self.currentQuality -= 1  # Diminui qualidade em 1

        # Se o tempo entre request e response for menor que 6 e maior ou igual a 5s
        elif (6 > self.deltaTimeLastChunk >= 5) and self.bufferSize > 8:
            if (self.currentQuality - 2) >= 0:
                self.currentQuality -= 2  # Diminui a qualidade em 2

        # Se o tempo entre request e response for maior do que 6s
        elif self.deltaTimeLastChunk >= 6 and self.bufferSize > 8:
            if (self.currentQuality - 3) >= 0:
                self.currentQuality -= 3  # Diminui a qualidade em 3

        # Se o tamanho de buffer for maior que 4s e menor que 8s
        elif 4 <= self.bufferSize < 8:
            self.currentQuality = self.currentQuality % 2  # Diminui a qualidade pela metade

        # Se o tamanho de buffer for menor que 4s
        elif self.bufferSize < 4:
            self.currentQuality = 0  # Diminui a qualidade para 0
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
