from datetime import datetime
import pyaudio
import wave
import _thread as th
import threading
import time
import os

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000

class recorder:
    def __init__(self):
        self.going = False # Variável de continuação do processo
        self.process_main = None # Thread principal
        self.process_time = None # Thread do tempo
        self.process_forced = None # Thread de interrupção forçada
        self.going_process_time = True # Fator de continuação da thread do tempo, para casos de interrupção forçada
        self.filename = "ScreenCapture.mpg" # Nome do arquivo
        self.next = False # Fator de definição para próxima gravaçãos
        self.interval = 60 # intervalo de tempo para cada gravação
        self.count = 0 # Contador para não ocorrer a sobrecarregação de arquivo
        self.time_total = '' # O tempo que irá dura

    def record(self, filename, time) -> None:
        try:
            if self.process.is_alive():
                self.going = False
        except AttributeError:
                print("Teste")

        # Abrindo processo de tempo
        self.time_total = time
        self.process_time = threading.Thread(target=self._time)
        self.process_time.start()

        # Definição de variáveis
        self.going = True
        self.filename = filename

        # Abrindo processo de captura de aúdio
        self.process_main = threading.Thread(target=self._record)
        self.process_main.start()
        
    def _next(self):
        time.sleep(self.interval)
        self.next = True

    # Thread para acabar de gravar quando o tempo acabar, entretanto, se o programa acabar forçadamente
    # essa thread acaba pelo valor do self.going_process_time ter sido invertido
    def _time(self):

        # Transformando o tempo pego em segundos para comparação posterior
        [hours, minutes] = self.time_total.split(':')
        seconds_total = int(hours) * 3600 + int(minutes) * 60

        while True:            
            if not self.going_process_time:
                break
            
            # Definindo meu tempo atual em segundos
            now = datetime.now()
            seconds_atual = now.hour * 3600 + now.minute * 60

            # Comparando o meu tempo determinado com o tempo atual, se sim, encerra o ciclo
            if (seconds_atual >= seconds_total): break
            time.sleep(1)
        
        self.going = False
        self.next = True

    def _record(self):
        p = pyaudio.PyAudio()

        os.system("cls")
        print("* Gravando..")
        
        while self.going:
            th.start_new_thread(self._next, ())

            stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=2)
            
            frames = []

            # Enquanto a função _next não definir que é para passar para o próximo, continue gravando
            while not self.next:
                
                # O try serve para evitar erros os quais acontecem quando o ciclo acaba e tenta capturar os dados
                # de aúdio ainda
                try:
                    data = stream.read(CHUNK)
                    frames.append(data)
                except  Exception as e:
                    print(e)

            # Terminando a gravação dessa parte, mas não finalizo o canal
            stream.stop_stream()
            stream.close()

            # Definindo o nome do arquivo com o contador para não sobreescrever o já existente
            filename = f'{self.filename}-{str(self.count)}.wav'

            wf = wave.open(filename, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            # Colocando o next como falso e aumentando o count para não sobreescrever o próximo arquivo de gravação
            self.next = False
            self.count += 1
        
        # Finalizo o canal
        p.terminate()

        # Caso tenha sido forçado o interrrupmento da gravação, a thread acaba
        if self.process_time.is_alive():
            self.going_process_time = False

        print("* Gravação concluída!")

    # Terminando a gravação forçadamente
    def stop_recording(self):
        self.going = False
        self.next = True

    # Capturando se o arquivo está continuando
    def get_going(self):
        return self.going

    # Capturo o valor do count atual
    def get_count(self):
        return self.count

if __name__ == "__main__":
    stream = recorder()
    stream.record('tmp/teste', 20)