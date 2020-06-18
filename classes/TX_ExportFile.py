from multiprocessing import Lock, Process, Queue, current_process
import queue # imported for using queue.Empty exception
from time import sleep
import timeit
from configparser import ConfigParser
import cv2
from pathlib import Path
import json

class ExportStream():
    def __init__(self, ConfigSection, configFile='classes\FileExportConfig.ini', frequency=1):
        config = ConfigParser()
        config.read(configFile)

        if not config.getboolean(ConfigSection, 'Work'):
            print('\nO módulo ' + str(ConfigSection) + ' do arquivo ' + str(configFile) + ' não está ativado!!!')
            print('Você pode ativar por meio da key "work" do arquivo .' + str(configFile)  + '\n')

        else:
            path           = config.get(ConfigSection, 'Path_of_files')
            fileType       = config.get(ConfigSection, 'Type_of_file')

            self.running   = Queue()
            self.tasks     = Queue()
            self.last_sent = 0

            if fileType == 'opencvImage':

                NamePatern = config.get(ConfigSection, 'Name').split(',')
                sep        = config.get(ConfigSection, 'Separator')
                ext        = config.get(ConfigSection, 'Extension')
                
                self.p = Process(name=str(ConfigSection), target=self.opencvImageExport, args=(path, NamePatern, sep, ext, self.tasks, frequency, self.running))
            
            elif fileType == 'json':
                name = config.get(ConfigSection, 'Name')
                ext  = config.get(ConfigSection, 'Extension')

                self.p = Process(name=str(ConfigSection), target=self.jsonExport, args=(path, name, ext, self.tasks, frequency, self.running))
    
    def start(self):
        self.p.start()

    def stop(self):
        print('O processo será interrompido.')
        self.running.put(False)
        
        self.p.join()
    
    def send(self, data):
        #print(data)

        self.last_sent = timeit.default_timer()

        self.tasks.put(data)
        #print(self.tasks)

    def opencvImageExport(self, filePath, namePatern, sep, ext, tasks, frequency, running):
        
        while running.empty() or not tasks.empty():
            try:
                task = tasks.get_nowait()
                #print('Essa é a tarefa:')
                #print(task)

            except queue.Empty:
                #print('Sem tarefas por enquanto, vou tirar uma soneca...')
                sleep(frequency)
                
            else:
                for opt_num, option in enumerate(namePatern):
                    
                    parameter = task[str(option).strip()]
                    if isinstance(parameter, float):
                        parameter = int(parameter)
                    
                    parameter = str(parameter)

                    if opt_num == 0:
                        fileName = parameter
                    else:
                        fileName = fileName + sep + parameter

                fileName = fileName + ext
                finalPath = Path(filePath, fileName)

                cv2.imwrite(str(finalPath), task['img_array'])

                #print('Eu salvei o arquivo ' + str(finalPath))
        
        print('O processo ' + str(current_process().name) + ' foi interrompido com sucesso.')

    def jsonExport(self, filePath, name, ext, tasks, frequency, running):
       
        while running.empty() or not tasks.empty():

            try:
                task = tasks.get_nowait()
                #print('Essa é a tarefa:')
                #print(task)

            except queue.Empty:
                #print('Sem tarefas por enquanto, vou tirar uma soneca...')
                sleep(frequency)
                
            else:

                finalPath = Path(filePath, name + ext)

                outfile = open(finalPath, 'w')
                
                json.dump(dict(task), outfile, indent=4, ensure_ascii=True)

                #print('Eu salvei o arquivo ' + str(finalPath))

        tasks.close()
        
        print('O processo ' + str(current_process().name) + ' foi interrompido com sucesso.')