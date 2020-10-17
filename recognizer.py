import speech_recognition as sr
import os

class Recognizer:
  def __init__(self):
    self.r = sr.Recognizer()
    self.count = 1

  # Lendo o arquivo ".waw"
  def read_file(self, filename):
    with sr.AudioFile(filename) as source:
      audio = self.r.record(source)

    return audio

  # Reconhecimento do arquivo com o audio gerado
  def recognize_speech(self, audio) -> str:
    try:
      text = self.r.recognize_google(audio, language="pt", show_all=True)

      os.system("cls")
      print(f"Reconhecimento... {self.count}")
      
      self.count += 1

      if text != []:
        return text['alternative'][0]['transcript']
      else:
        return '' 
      
    except sr.RequestError as e:
      print(f"Erro de conexão: {e}")

      self.count += 1
      
      return ''
    
