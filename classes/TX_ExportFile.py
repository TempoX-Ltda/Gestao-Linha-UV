from multiprocessing import Lock, Process, Queue, current_process
import queue # imported for using queue.Empty exception
from time import sleep
import timeit
from configparser import ConfigParser
import cv2
from pathlib import Path

class ExportStream():
    def __init__(self, ConfigSection, configFile='classes\FileExportConfig.ini', frequency=1):
        config = ConfigParser()
        config.read(configFile)

        self.work       = config.getboolean(ConfigSection, 'Work')
        self.path       = config.get(ConfigSection, 'Path_of_files')
        self.NamePatern = config.get(ConfigSection, 'Name').split(',')
        self.sep        = config.get(ConfigSection, 'Separator')
        self.ext        = config.get(ConfigSection, 'extension')
        fileType        = config.get(ConfigSection, 'Type_of_file')

        self.frequency = frequency
        self.running = Queue()
        self.tasks = Queue()
        self.last_sent = 0

        if fileType == 'opencvImage':
            self.p = Process(target=self.opencvImageExport, args=(self.path, self.NamePatern, self.sep, self.ext, self.tasks, frequency, self.running))
        
        elif fileType == 'text':
            self.p = Process(target=self.textExport, args=(self.path, self.NamePatern, self.sep, self.ext, self.tasks, frequency, self.running))
        
        elif fileType == 'json':
            self.p = Process(target=self.jsonExport, args=(self.path, self.NamePatern, self.sep, self.ext, self.tasks, frequency, self.running))
    
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
        print(self.tasks)

    def opencvImageExport(self, filePath, namePatern, sep, ext, tasks, frequency, running):
        
        while running.empty():
            try:
                task = tasks.get_nowait()
                #print('Essa é a tarefa:')
                #print(task)

            except queue.Empty:
                #print('Sem tarefas por enquanto, vou tirar uma soneca...')
                sleep(frequency)
                
            else:
                fileName = ''
                for opt_num, option in enumerate(namePatern):
                    
                    parameter = task[str(option).strip()]
                    if isinstance(parameter, float):
                        parameter = int(parameter)
                    
                    parameter = str(parameter)

                    if opt_num == 0:
                        fileName = fileName + parameter
                    else:
                        fileName = fileName + sep + parameter

                fileName = fileName + ext
                finalPath = Path(filePath, fileName)

                cv2.imwrite(str(finalPath), task['img_array'])

                print('Eu salvei o arquivo ' + str(finalPath))
        
        print('O processo foi interrompido com sucesso.')

    def textExport(self, Type, filePath, namePatern, sep, ext, tasks, frequency, running):
        pass
    
    def jsonExport(self, Type, filePath, namePatern, sep, ext, tasks, frequency, running):
        pass