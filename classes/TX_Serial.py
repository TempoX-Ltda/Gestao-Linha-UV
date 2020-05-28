from multiprocessing import Lock, Process, Queue, current_process
import queue # imported for using queue.Empty exception
import serial
from time import sleep
import timeit
class SerialStream():
    def __init__(self, COM_Port, upload_frequency, Baudrate=9600, timeout=5):
        self.upload_frequency = upload_frequency
        self.running = Queue()
        self.tasks = Queue()
        self.p = Process(target=self.SerialStream, args=(COM_Port, upload_frequency, self.tasks, Baudrate, timeout, self.running))
        self.last_sent = 0
        
    def start(self):
        self.p.start()

    def stop(self):
        print('O processo serial será interrompido.')
        self.running.put(False)
        self.p.join()
    
    def send(self, data):
        print(data)

        self.last_sent = timeit.default_timer()

        self.tasks.put(data)

    def SerialStream(self, COM_Port, upload_frequency, tasks, Baudrate, timeout, running):

        self.ser = serial.Serial(COM_Port, Baudrate, timeout)
        self.loop(tasks, upload_frequency, running, self.ser)

    def loop(self, tasks, upload_frequency, running, ser):
        while running.empty():
            
            try:
                task = tasks.get_nowait()

            except queue.Empty:
                print('Sem tarefas por enquanto, vou tirar uma soneca...')
                sleep(upload_frequency)
            
            else:
                ser.write(bytes(task, 'utf-8'))
                print('Eu escrevi ' + str(task) + ' na porta ' + ser.name)
        
        print('O processo serial foi interrompido com sucesso.')


if __name__ == '__main__':
    tasks = Queue()

    Serial = SerialStream('COM1', 0.5, Baudrate=9600, timeout=5)

    Serial.start()

    Serial.send('ola tudo bem? end')
 
    sleep(5)

    Serial.send('ola222123 tudo bem? end')

    sleep(5)

    Serial.stop()
