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
from trafico import Trafico, TraficoNormal, TraficoAtaque
from netstat import netstat

BAN_CPU_MEASURE = True   # Bandera que indica que se esta llevando a cabo una medicion de CPU

def getPIDElements(port = 6653):
    pl = subprocess.Popen(['ps', '-ax','-o','pid,cmd'], stdout=subprocess.PIPE).communicate()[0]
    lines = pl.split('\n')
    mininet_lines = []
    for l in lines:
        if "mininet" in l:
            mininet_lines.append(l)
    # print mininet_lines
    dicProcesos = {}
    for p in mininet_lines:
        l = p.split()
        if ("h" in l[-1]) or ("s" in l[-1]):        
            # Agregando hosts y el swith
            node = l[-1]
            dicProcesos[node[node.find(':')+1:]] = int(l[0])
    # Agregando el controlador
    for conn in netstat():
        # print conn
        if str(port) in conn[2] and ('0.0.0.0' in conn[2]):
            dicProcesos['c0'] = int(conn[5]) 
    return dicProcesos

class TopologiaTest(Topo):
    def __init__(self, bw = 100):
        # Initialize topology
        setLogLevel("info")
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

ue_ryu = UnidadExperimental(topo=TopologiaTest(bw = 100),controller=RYU('c0'))
ue_ryu.definirNodosClaves('h1','h2','h3')

ue_pox = UnidadExperimental(topo=TopologiaTest(bw = 100),controller=POX('c0'))
ue_pox.definirNodosClaves('h1','h2','h3')



def monitoring_ping_normal(ue,nombreArchivo = None):
    # Parametros de la unidad experimental
    setLogLevel("info")
    info("Configurando unidad experimental\n")
    info("Configurando trafico normal\n")
    info("Configurando la red\n")
    net = Mininet(topo = ue.getTopo(), controller=ue.getController(), link=TCLink, build=False)
    info("wait 5s ...\n")
    sleep(5) # Dando un tiempo de espera para que el controlador arranque
    net.build()
    # Configurando clase asociada al trafico
    info("Configurando clase asociada al trafico\n")    
    [A,C,V] = ue.obtenerNodosClaves()
    # ---- info("%s %s %s\n"%(A,C,V))
    C = net.get(C)
    V = net.get(V)
    t_normal = TraficoNormal(C,V)    
    net.start()
    info("wait 5s ...\n")
    sleep(5)
    dicProcesos = getPIDElements()
    name_procesos = dicProcesos.keys()
    pids_procesos = dicProcesos.values()
    f = open("cpu_measure.log","w+")
    title_procesos = str(name_procesos).strip("[]")
    title_procesos = title_procesos.replace(', ',';')
    f.write(title_procesos + "\n")
    args_timer = dicProcesos.items() + [f]
    TIEMPO = 1
    timer = threading.Timer(TIEMPO, getCPUMeasure, args = args_timer)
    timer.start()
    net.getNodeByName('c0').cmd("tcpdump -i any -nn port 6653 -U -w mylog &")
    net.pingAll()
    t_normal.pingMeasure(filename = nombreArchivo) # Llevando salida a un archivo
    BAN_CPU_MEASURE = False
    #CLI(net)
    
    info("wait 2s ...\n")
    sleep(2)
    
    #timer.join()
    net.stop() 
    f.close()    
    net.getNodeByName('c0').cmd("pkill tcpdump")


def monitoring_ping_ataque(ue,nombreArchivo = None):
    # Parametros de la unidad experimental
    setLogLevel("info")
    info("Configurando unidad experimental\n")
    info("Configurando trafico normal\n")
    info("Configurando la red\n")
    net = Mininet(topo = ue.getTopo(), controller=ue.getController(), link=TCLink, build=False)
    info("wait 5s ...\n")
    sleep(5) # Dando un tiempo de espera para que el controlador arranque
    net.build()
    # Configurando clase asociada al trafico
    info("Configurando clase asociada al trafico\n")    
    [A,C,V] = ue.obtenerNodosClaves()
    # ---- info("%s %s %s\n"%(A,C,V))
    A = net.get(A)
    C = net.get(C)
    V = net.get(V)
    t_ataque = TraficoAtaque(A,C,V)   
    net.start()
    info("wait 5s ...\n")
    sleep(5)
    dicProcesos = getPIDElements()
    name_procesos = dicProcesos.keys()
    pids_procesos = dicProcesos.values()
    f = open("cpu_measure.log","w+")
    title_procesos = str(name_procesos).strip("[]")
    title_procesos = title_procesos.replace(', ',';')
    f.write(title_procesos + "\n")
    args_timer = dicProcesos.items() + [f]
    TIEMPO = 1
    timer = threading.Timer(TIEMPO, getCPUMeasure, args = args_timer)
    timer.start()
    net.getNodeByName('c0').cmd("tcpdump -i any -nn port 6653 -U -w mylog &")
    net.pingAll()
    t_ataque.pingMeasure(filename = nombreArchivo) # Llevando salida a un archivo
    BAN_CPU_MEASURE = False
    #CLI(net)
    
    info("wait 2s ...\n")
    sleep(2)
    
    #timer.join()
    net.stop() 
    f.close()    
    net.getNodeByName('c0').cmd("pkill tcpdump")



# Problema - Solo es llamado una sola vez  ---- https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/
def getCPUMeasure(*args):
    setLogLevel("info")
    try:
        global BAN_CPU_MEASURE
        while BAN_CPU_MEASURE == True:    
            if BAN_CPU_MEASURE == False:
                info("Termiando medicion de la CPU...")  
                break    
            #print('*')
            sleep(1)  # Lleva a cabo una medida cada segundo
            measure_cpu = ''
            for arg in args[:-1]:
                p = psutil.Process(arg[1])
                cpu_p = p.cpu_percent()
                measure_cpu = measure_cpu + str(cpu_p) + ";"
            measure_cpu = measure_cpu.rstrip(';')
            args[-1].write(measure_cpu + "\n") 
    except psutil.NoSuchProcess:
        info("Termiando medicion de la CPU...")        
        


if __name__ == "__main__":
    # monitoring_ping_normal(ue_ryu,'ping_normal_ryu.log')
    # monitoring_ping_ataque(ue_ryu,'ping_ataque_ryu.log')
    # monitoring_ping_normal(ue_pox,'ping_normal_pox.log')
    monitoring_ping_ataque(ue_pox,'ping_ataque_pox.log')
    
