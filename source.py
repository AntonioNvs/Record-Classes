import os
from record import recorder

class Source:

    # Construindo um arquivo .txt para os dados
    def constructor(self, filename, _class, text):
        # Pegando o intervalo para definir o tempo que foi falado cada frase
        stream = recorder()
        interval = stream.interval

        exist = False
        for src in os.listdir('data'):
            if src == _class:
                exist = True
        
        if not exist:
            os.mkdir('data/' + _class)

        with open(f'data/{_class}/{filename}.txt', 'w', encoding='utf-8') as archive:
            count = 0
            for phrase in text:
                horas = int(interval * count/3600)
                horas = str(horas) if horas >= 10 else f"0{str(horas)}"

                # Definição dos minutos
                minutos = int((interval * count % 3600)/60)
                minutos = str(minutos) if minutos >= 10 else f"0{str(minutos)}"

                # Definição dos segundos
                segundos = interval * count % 60
                segundos = str(segundos) if segundos >= 10 else f"0{str(segundos)}"

                time = f'{horas}:{minutos}:{segundos}'

                archive.write(time + ': ' + phrase + '\n')
                count += 1
    
    # Deletando todos os arquivos de uma pasta, no caso a pasta de gravação
    def delete(self):
        [os.remove(f'tmp/{file}') for file in os.listdir('tmp')]

    def search(self, past, key_words):
        sources = os.listdir(f'data/{past}')
        
        result = []
        for archive in sources:
            with open(f'data/{past}/{archive}', 'r', encoding='utf-8') as src:
                lines = src.read().splitlines()
                for line in lines:
                    for word in key_words:
                        if word in line:
                            index = line.index(word)
                            dictionary = {
                                'title': f'{archive} - Palavra: {word} - Linha: {str(lines.index(line) + 1)}',
                                'phrarse': line[index-20:index+len(word)+20],
                                'time': line[:8]
                            }
                            result.append(dictionary)
        
        return result
                            

if __name__ == "__main__":
    test = Source()

    test.search('Senai', ['código', 'gravando'])