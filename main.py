from time import sleep
from datetime import datetime
from os import path, listdir
from recognizer import Recognizer
from record import recorder
from source import Source
import os
import threading

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy import Config
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

Config.set('graphics', 'multisamples', '0')

class SearchScreen(ScrollView):
    def __init__(self, **kwargs):
            super().__init__(**kwargs)

            # Elementos de pesquisa
            self.label_search = Label(text='Coloque a/as palavras a serem pesquisadas', font_size=30, size_hint_y=0.5)
            self.input_search = TextInput(size_hint_y=0.5)
            self.label_source = Label(text='Nome da pasta onde será pesquisado', font_size=30)
            self.input_source = TextInput(size_hint_y=0.5)
            self.button_screen_search = Button(text='Pesquisar', on_release=self.search)

            self.clear_widgets()
            self.layout = BoxLayout(orientation='vertical')

            self.layout.add_widget(self.label_search)
            self.layout.add_widget(self.input_search)
            self.layout.add_widget(self.label_source)
            self.layout.add_widget(self.input_source)
            self.layout.add_widget(self.button_screen_search)

            self.add_widget(self.layout)

    # Indo para tela do resultado enviando as palavras chaves
    def search(self, _):
        text_source = self.input_source.text
        text_search = self.input_search.text

        # Verificando se os inputs não estão vazios e se existe a pasta no database
        if  text_search != '' and any(text_source == i for i in os.listdir('data')):
            result = ResultSearchScreen(text_search, text_source)

            self.remove_widget(self.layout)

            self.add_widget(result)

class ResultSearchScreen(ScrollView):
    def __init__(self, words, source, **kwargs):
            super().__init__(**kwargs)
            
            self.words = words.split(' ')
            self.src = source

            # Criando os componentes
            self.source = Source()
            self.layout = BoxLayout(orientation='vertical')
            self.clear_widgets()

            results = self.search()

            if results != []:
                for result in results:
                    title = Label(text=result['title'], font_size=30, size_hint_y=None, height=40)
                    time = Label(text=result['time'], font_size=20, size_hint_y=None, height=40)
                    phrarse = Label(text=result['phrarse'], font_size=15, size_hint_y=None, height=40)
                    separator = Label(text='-----------------------------------------------', font_size=60, size_hint_y=None, height=20)

                    
                    self.layout.add_widget(title)
                    self.layout.add_widget(time)
                    self.layout.add_widget(phrarse)
                    self.layout.add_widget(separator)
            
            self.add_widget(self.layout)

    # Pesquisando no database
    def search(self):
        return self.source.search(self.src, self.words)

class RecordOptionsScreen(ScrollView):
    def __init__(self, **kwargs):
            super().__init__(**kwargs)

            # Elementos de inicial de gravacao
            self.label_name = Label(text='Qual a matéria que irá ser gravada?', font_size=24)
            self.label_date = Label(text='Qual o horário que você quer que acabe automaticamente? (HH:MM)', font_size=24)
            self.input_name = TextInput(height=56)
            self.input_date = TextInput(height=56)
            self.button_start_or_stop_record = Button(text='Começar a gravar', on_release=self._record)
            self.layout = BoxLayout(orientation='vertical')

            self.clear_widgets()
            self.layout.add_widget(self.label_name)
            self.layout.add_widget(self.input_name)
            self.layout.add_widget(self.label_date)
            self.layout.add_widget(self.input_date)
            self.layout.add_widget(self.button_start_or_stop_record)
            self.add_widget(self.layout)

    def _record(self, _):
        self.clear_widgets()

        # Pegando os valores dos campos
        name = self.input_name.text
        date = self.input_date.text

        if (name != '' and date != ''):
            screen_recorder = RecordScreen(name=name, date=date)
            self.add_widget(screen_recorder)


class RecordScreen(ScrollView):
    def __init__(self, name, date, **kwargs):
            super().__init__(**kwargs)

            # Demonstrar gravação
            self.label_time = Label(text='00:00:00', font_size=42)
            self.stop_record = Button(text='Parar de gravar', on_release=self.stop)

            self.name = name.capitalize()
            self.date = date
            self.stream = recorder()
            self.layout = BoxLayout(orientation='vertical')

            # Chamando função de gravação
            threading.Thread(target=self._record).start()

            # Adicionando elementos
            self.clear_widgets()
            self.layout.add_widget(self.label_time)
            self.layout.add_widget(self.stop_record)

            self.add_widget(self.layout)

    def next_screen(self, wave, number): 
        self.remove_widget(self.layout)
        self.add_widget(RecognitionScreen(wave, number))

    def _time(self):
        seconds = 0
   
        while self.stream.process_main.is_alive():
            # Definição das horas
            horas = int(seconds/3600)
            horas = str(horas) if horas >= 10 else f"0{str(horas)}"

            # Definição dos minutos
            minutos = int((seconds % 3600)/60)
            minutos = str(minutos) if minutos >= 10 else f"0{str(minutos)}"

            # Definição dos segundos
            segundos = seconds % 60
            segundos = str(segundos) if segundos >= 10 else f"0{str(segundos)}"

            # Printando e salvando o valor na variável global da classe
            self.label_time.text = f'{horas}:{minutos}:{segundos}'

            sleep(1)
            seconds += 1


    def _record(self):

        # Definindo o meu dia atual s
        now = datetime.now()
        dia_atual = f'{now.day}-{now.month}-{now.year}'

        # Definindo o caminho de gravação
        WAVE_OUTPUT_FILENAME = f"tmp/{self.name}-{dia_atual}"
        filename = path.join(path.dirname(path.realpath(__file__)), WAVE_OUTPUT_FILENAME)

        self.stream.record(filename, self.date)
        threading.Thread(target=self._time).start()

        # Enquanto a thread estiver ativa, não continue o processo e atualize o tempo na tela
        while self.stream.process_main.is_alive():
            pass
        
        # Descobrindo qual foi o maior arquivo que foi gravado
        number = self.stream.get_count()
        
        # Indo para Classe de reconhecimento
        self.next_screen(WAVE_OUTPUT_FILENAME, number)

    def stop(self, _):
        self.stream.stop_recording()


class RecognitionScreen(ScrollView):
    def __init__(self, filename, count, **kwargs):
        super().__init__(**kwargs)

        self.filename = filename
        self.count = count
        self.recog = Recognizer()
        
        # Elemento de reconhecimento
        self.label_recognition = Label(text=f'Reconhecimento 1 de {self.count}', font_size=30)
        self.clear_widgets()
        self.layout = BoxLayout(orientation='vertical')

        # Inicializando thread de reconhecimento
        threading.Thread(target=self._recognition).start()

        self.layout.add_widget(self.label_recognition)
        self.add_widget(self.layout)

    def _recognition(self):
        # Colocando no banco de dados
        text = []

        # Para cada arquivo, um reconhecimento
        for i in range(self.count):
            # Informando qual reconhecimento está sendo realizado
            self.label_recognition.text = f'Reconhecimento {i+1} de {self.count}'

            # Lendo o arquivo de aúdio
            audio = self.recog.read_file(f'{self.filename}-{i}.wav')

            # Fazendo o STT
            text_recognition = self.recog.recognize_speech(audio)
            text.append(text_recognition)

            sleep(0.1)

        self.label_recognition.text = "Reconhecimento concluído, salvando o arquivos"
        organizator = Source()
        organizator.delete()

        # Definindo o meu dia atual
        now = datetime.now()
        dia_atual = f'{now.day}-{now.month}-{now.year}'

        # Definindo nome
        name = self.filename.replace('tmp/', '').replace(dia_atual ,'').replace('-', '')

        organizator.constructor(f'{dia_atual}-{str(now.hour)}-{str(now.minute)}', name, text)

        self.remove_widget(self.layout)
        self.add_widget(Initial())


class Initial(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Criando os elementos inicias
        self.button_record = Button(text='Gravar', on_release=self.record)
        self.button_search = Button(text='Pesquisar', on_release=self.search)

        # Adicionando os elementos atuais
        self.add_widget_initial()

    def add_widget_initial(self):
        self.layout = BoxLayout(orientation='vertical')
        self.clear_widgets()

        self.layout.add_widget(self.button_search)
        self.layout.add_widget(self.button_record)
        self.add_widget(self.layout)

    def search(self, trash):
        self.clear_widgets()
        
        screen_search = SearchScreen()
        self.add_widget(screen_search)

    def record(self, trash):
        self.clear_widgets()
        screen_recorder_options = RecordOptionsScreen()
        self.add_widget(screen_recorder_options)

    
class AppRecorder(App):
    def build(self):
        layout = Initial()

        root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        root.add_widget(layout)

        return root

AppRecorder().run()