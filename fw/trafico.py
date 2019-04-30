import os
from mininet.net import Mininet
from mininet.log import info, setLogLevel
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.link import TCLink
from mininet.topo import Topo, SingleSwitchTopo
import subprocess
from time import time, sleep
import psutil
from mininet.cli import CLI
from subprocess import Popen, PIPE, STDOUT
from select import poll, POLLIN
import threading
import signal
from mininet.topolib import TreeTopo 
from controlador import RYU, POX
from unidadExperimental import UnidadExperimental
from mininet.link import TCLink



TIEMPO_ADICIONAL = 4

class Trafico:
    # Se inicia objetos tipo nodo
    def __init__(self, src = None, dst = None):
        self.src = src
        self.dst = dst
                
    def obtenerNodoFuente(self):
        return self.src

    def obtenerNodoDestino(self):
        return self.dst

class TraficoNormal(Trafico):
    def __init__(self, src = None, dst = None):
        self.timer = None
        Trafico.__init__(self, src = src, dst = dst)

    def pingMeasure(self,
                    h_src = None,
                    h_dst = None,
                    veces = 10,
                    intervalo = 1.0,
                    filename = None):

        h_C = h_src
        h_V = h_dst
        if h_src == None and h_dst == None:
            h_C = self.src
            h_V = self.dst
        if filename == None:
            info("Starting Pings: %s ---> %s\n" % (str(h_C.IP()), str(h_V.IP())))            
            h_C.cmdPrint('ping -c', veces, '-i', intervalo, str(h_V.IP()))
            info("End pings ***\n")
        else:
            info("Starting Pings: %s ---> %s\n" % (str(h_C.IP()), str(h_V.IP())))            
            logfile = open(filename, 'w')
            info("Open file: %s\n"%filename)
            ping_process = h_C.popen(['ping', str(h_V.IP()),
                           '-i', str(intervalo),
                           '-c', str(veces)],
                          stdout=PIPE)
            for line in ping_process.stdout:
                logfile.write(line)
            ping_process.wait()
            logfile.close()
            info("End pings ***\n")
    
    def iperfMeasure(self,
                     h_src = None,
                     h_dst = None,
                     intervalo=1,
                     tiempo=10,
                     filename=None
                     ):
        h_C = h_src
        h_V = h_dst
        if h_src == None and h_dst == None:
            h_C = self.src
            h_V = self.dst
        if filename == None:
            # Cuando hay nombre de archivo
            info("Starting iperf server in %s\n"%(str(h_V.IP()))) 
            # Proceso hijo
            iperf_server_process = h_V.popen(['iperf', '-s'])
            if iperf_server_process != 0:
                # Proceso padre
                info("Starting iperf client in %s\n"%(str(h_C.IP())))
                h_C.cmdPrint('iperf', '-c', h_V.IP(), '-i', intervalo, '-t ', tiempo)
                iperf_server_process.kill()
                info("End iperf measure ***\n")
        else:
            info("Starting iperf server in %s\n"%(str(h_V.IP()))) 
            # Proceso hijo
            iperf_server_process = h_V.popen(['iperf', '-s'])
            if iperf_server_process != 0:
                info("Starting iperf client in %s\n"%(str(h_C.IP())))
                info("Open file: %s\n"%filename)
                h_C.cmd('iperf', '-c', h_V.IP(), '-i', intervalo, '-t ', tiempo, '>', filename)
                iperf_server_process.kill()                
                info("End iperf measure ***\n")
                
class TraficoAtaque(Trafico):
    def __init__(self, atk = None,src = None, dst = None, tipo_ataque = 1):
        Trafico.__init__(self, src = src, dst = dst)
        self.atk = atk
        self.tipo_ataque = tipo_ataque # 1. Flooding and spoofing
        self.timer = None
        self.timer_atk = None
        self.process_attack = None

    def pingMeasure(self,
                    h_atk = None,
                    h_src = None,
                    h_dst = None,
                    veces = 10,
                    intervalo = 1.0,
                    t_inicio_atk = 4,
                    filename = None):
        h_C = h_src
        h_V = h_dst
        h_A = h_atk
        if h_src == None and h_dst == None and h_atk == None:
            h_C = self.src
            h_V = self.dst
            h_A = self.atk
            if self.tipo_ataque == 1:
                if filename != None:
                    info("Starting pings ***\n")
                    # Lanzando el ping
                    log = open(filename,'w')
                    ping_process = h_C.popen(['ping', '-c', str(veces), '-i', str(intervalo), h_V.IP()],stdout=log, stderr=log, shell=True)
                    if ping_process != 0:
                        # Parte que lanza el ataque
                        self.timer_atk = threading.Timer(t_inicio_atk, self.launchAttack)
                        self.timer_atk.start()
                    else:
                        #ping_process.wait()
                        # Timer que killea ping y el ataque
                        self.timer = threading.Timer(veces + TIEMPO_ADICIONAL, self.killPing, 
                                                                 args=[ping_process] )
                        self.timer.start()
                        self.timer.join() 
                    ping_process.wait() 
                    info("End pings ***\n")
                    # Terminando el ataque despues de que se acaba la medicion del ping
                    info("End attack ***\n")   
                         
                else:
                    info("No implementada")


    def iperfMeasure(self,
                        h_atk = None,
                        h_src = None,
                        h_dst = None,
                        intervalo = 1,
                        tiempo = 10,
                        t_inicio_atk = 4,
                        filename = None
                        ):
            # Es obligatorio poner el nombre del archivo
            h_C = h_src
            h_V = h_dst
            h_A = h_atk
            if h_src == None and h_dst == None and h_atk == None:
                h_C = self.src
                h_V = self.dst
                h_A = self.atk
                if self.tipo_ataque == 1:
                    info("++++++ Ataque DoS por flooding y spoofing +++++\n")
                    if filename != None:
                        log = open(filename,'w')
                        info("Starting iperf server\n")                    
                        server_process = h_V.popen(['iperf', '-s'])  # Victima  (Servidor)
                        if server_process != 0:
                            info("Starting iperf client\n")
                            client_process = h_C.popen(['iperf', '-c',
                                                        str(h_V.IP()),'-i',str(intervalo),
                                                        '-t',str(tiempo)],stdout=log, stderr=log, shell=True)
                            info("Starting iperf measure\n")                                                    
                            if client_process != 0:
                                # Lanzar timer para ataque   
                                self.timer_atk = threading.Timer(t_inicio_atk, self.launchAttack)
                                self.timer_atk.start()
                                #self.timer.join()               

                                self.timer = threading.Timer(tiempo + TIEMPO_ADICIONAL, self.killIperfClient, 
                                                                 args=[client_process,server_process] )
                                self.timer.start()
                                self.timer.join()
                                info("End iperf measure\n")
                    else:
                        info("Es necesario colocar un nombre de archivo a la entrada para almacenar los resultados\n")
                        # Nota: Mirar si con cmdPrint se puede obtener el pid para killearlo como en el caso de Popen
                        # Puede que last pid sirva?

    def killIperfClient(self,p1,p2):
        p1.kill()
        p2.kill()
        self.attack_process.kill()
        self.timer.cancel()

    def killPing(self,p1):
        # kill del proceso del ping
        p1.kill()
        # kill del proceso del ataque
        self.attack_process.kill()
        self.timer.cancel()


    def launchAttack(self):
        info("Launch attack: %s ---> %s\n" % (str(self.atk.IP()), str(self.dst.IP())))
        self.attack_process = self.atk.popen(['hping3', '--flood',
                                    '--rand-source',
                                    self.dst.IP()])  # Atacante
        if self.attack_process != 0:
            self.timer_atk.cancel()


        


ue1 = UnidadExperimental(topo=SingleSwitchTopo(k = 3, bw = 100),controller=RYU('c0'))
ue1.definirNodosClaves('h1','h2','h3')

ue2 = UnidadExperimental(topo=SingleSwitchTopo(k = 3, bw = 100),controller=POX('c0'))
ue2.definirNodosClaves('h1','h2','h3')

class TopologiaTest(Topo):
    def __init__(self, bw = 100):
        # Initialize topology
        Topo.__init__(self)
        self.bw = bw
        h1 = self.addHost('h1', ip='10.0.0.1')  # Cliente
        h2 = self.addHost('h2', ip='10.0.0.2')  # Atacante
        h3 = self.addHost('h3', ip='10.0.0.3')  # Victima

        # Add switches
        info('*** Adding switches\n')
        s1 = self.addSwitch('s1', protocols='OpenFlow13')

        # Add links
        info('*** Creating links\n')
        self.addLink(h1, s1, bw = self.bw)
        self.addLink(h2, s1, bw = self.bw)
        self.addLink(h3, s1, bw = self.bw)

ue3 = UnidadExperimental(topo=TopologiaTest(100),controller=RYU('c0'))
ue3.definirNodosClaves('h1','h2','h3')

ue4 = UnidadExperimental(topo=TopologiaTest(100),controller=POX('c0'))
ue4.definirNodosClaves('h1','h2','h3')

def test_ping_normal(ue,nombreArchivo = None):
    # Parametros de la unidad experimental
    setLogLevel("info")
    info("Configurando unidad experimental\n")
    info("Configurando trafico normal\n")
    info("Configurando la red\n")
    net = Mininet(topo = ue.getTopo(),controller=ue.getController(),build=False)
    net.build()
    # Configurando clase asociada al trafico
    info("Configurando clase asociada al trafico\n")    
    [A,C,V] = ue.obtenerNodosClaves()
    # ---- info("%s %s %s\n"%(A,C,V))
    C = net.get(C)
    V = net.get(V)
    t_normal = TraficoNormal(C,V)
    # Arrancando la red
    net.start()
    net.pingAll()
    # t_normal.pingMeasure() # Mostrando salida en pantalla
    t_normal.pingMeasure(filename = nombreArchivo) # Llevando salida a un archivo
    CLI(net)
    net.stop()

def test_iperf_normal(ue,nombreArchivo = None):
    # Parametros de la unidad experimental
    setLogLevel("info")
    info("Configurando unidad experimental\n")
    info("Configurando trafico normal\n")
    info("Configurando la red\n")
    net = Mininet(topo = ue.getTopo(), controller=ue.getController(), link=TCLink ,build=False)
    net.build()
    # Configurando clase asociada al trafico
    info("Configurando clase asociada al trafico\n")    
    [A,C,V] = ue.obtenerNodosClaves()
    # ---- info("%s %s %s\n"%(A,C,V))
    C = net.get(C)
    V = net.get(V)
    t_normal = TraficoNormal(C,V)
    # Arrancando la red
    net.start()
    net.pingAll()
    t_normal.iperfMeasure(filename = nombreArchivo) # Llevando salida a un archivo
    CLI(net)
    net.stop()

def test_iperf_ataque(ue,t_medida = 10, t_start_ataque = 4,nombreArchivo = None):
    # Parametros de la unidad experimental
    setLogLevel("info")
    info("Configurando unidad experimental\n")
    info("Configurando trafico normal\n")
    info("Configurando la red\n")
    net = Mininet(topo = ue.getTopo(), controller=ue.getController(), link=TCLink ,build=False)
    net.build()
    info("Waiting 5 seconds...\n")
    sleep(5)
    # Configurando clase asociada al trafico
    info("Configurando clase asociada al trafico\n")    
    [A,C,V] = ue.obtenerNodosClaves()
    A = net.get(A)
    C = net.get(C)
    V = net.get(V)
    t_ataque = TraficoAtaque(A,C,V)
    # Arrancando la red
    net.start()
    net.pingAll()
    t_ataque.iperfMeasure(filename = nombreArchivo, tiempo=t_medida,t_inicio_atk=t_start_ataque) # Llevando salida a un archivo
    CLI(net)
    net.stop()

def test_ping_ataque(ue,t_medida = 10, t_start_ataque = 4,nombreArchivo = None):
    # Parametros de la unidad experimental
    setLogLevel("info")
    info("Configurando unidad experimental\n")
    info("Configurando trafico normal\n")
    info("Configurando la red\n")
    net = Mininet(topo = ue.getTopo(), controller=ue.getController(), link=TCLink ,build=False)
    net.build()
    info("Waiting 5 seconds...\n")
    sleep(5)
    # Configurando clase asociada al trafico
    info("Configurando clase asociada al trafico\n")    
    [A,C,V] = ue.obtenerNodosClaves()
    A = net.get(A)
    C = net.get(C)
    V = net.get(V)
    t_ataque = TraficoAtaque(A,C,V)
    # Arrancando la red
    net.start()
    net.pingAll()
    t_ataque.pingMeasure(filename = nombreArchivo,veces=t_medida,t_inicio_atk=t_start_ataque)
    CLI(net)
    info("chao")
    net.stop()


if __name__ == "__main__":
    info("*** Funciones de prueba ***\n")
    # test_ping_normal(ue1,'ping_normal_ryu.log')
    # test_ping_normal(ue2,'ping_normal_pox.log')
    # test_ping_ataque(ue1,'ping_ataque_ryu.log')
    # test_ping_ataque(ue2,'ping_ataque_pox.log')
    # test_iperf_normal(ue3,'iperf_normal_ryu.log')
    # test_iperf_normal(ue4,'iperf_normal_pox.log')
    test_ping_ataque(ue4,t_medida=20,t_start_ataque=5,nombreArchivo = 'ping_ataque_pox.log')
    #test_iperf_ataque(ue3,t_medida=20,t_start_ataque=5,nombreArchivo = 'iperf_ataque_ryu.log')
    #test_iperf_ataque(ue4,t_medida=20,t_start_ataque=5,'iperf_ataque_pox.log')



    







