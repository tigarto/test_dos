from disenoExperimental import obtenerTratamientos, obtenerNumeroTratamientos, codificarTratamientos, \
                               crearMatrixReplicas, definirOrdenTratamientos
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
from topologia import TopologiaTest
from trafico import Trafico, TraficoNormal, TraficoAtaque
from netstat import netstat

DEBUG = True
mediciones = ['iperf-tcp','ping']


if __name__ == "__main__":
    print("************************ DEFINIENDO EL DISEÑO EXPERIMENTAL ************************\n") 
    niveles = { 
                'controlador': ['ryu','pox'],
                'trafico': ['normal','ataque']
              }
    tr = obtenerTratamientos(niveles)
    tr_cod = codificarTratamientos(niveles)
    n_tr = obtenerNumeroTratamientos(tr_cod)
    m = crearMatrixReplicas(n_tr,1)
    ot = definirOrdenTratamientos(m,tr_cod)
    if DEBUG:
        for e in ot:
            print e

    """
    ['ryu', 'ataque2']
    ['pox', 'ataque2']
    ['ryu', 'ataque2']
    ['pox', 'ataque2']

    """

    print("\n********************** GENERANDO LAS UNIDADES EXPERIMENTALES ***********************\n")
    topoTest=TopologiaTest(bw = 100)
    print("Definiendo topologia test...\n")
    sleep(1)
    print("* Topologia test definida...\n")
    sleep(1)
    print("Definiendo controladores...\n")
    c_Ryu=RYU('c0')
    sleep(1)
    print("* Controlador Ryu definido...\n")
    controller=POX('c0')
    c_POX=POX('c0')
    sleep(1)
    print("* Controlador POX definido...\n")
    print("Generando combinacion \"Controlador + Topologia\" para el test...\n")

    # Experimentos 

    for e in ot:
        # Definiendo la red con el controlador
        if e[0] == 'ryu':
            ue = UnidadExperimental(topo=topoTest,controller=c_Ryu)
            ue.definirNodosClaves('h1','h2','h3')
            net = Mininet(topo = ue.getTopo(), controller=ue.getController(), link=TCLink, build=False)
        elif e[0] == 'pox':
            ue = UnidadExperimental(topo=topoTest,controller=c_POX)
            ue.definirNodosClaves('h1','h2','h3')
            net = Mininet(topo = ue.getTopo(), controller=ue.getController(), link=TCLink, build=False)
        info("wait 5s ...\n")
        sleep(5) # Dando un tiempo de espera para que el controlador arranque
        net.build()
        # Configurando clase asociada al trafico
        info("Configurando clase asociada al trafico\n")    
        [A,C,V] = ue.obtenerNodosClaves()
        A = net.get(A)
        C = net.get(C)
        V = net.get(V)
        # Determinando el trafico a emplear
        """
        Pendiente:
        1. Repeticiones.
        2. Mediciones: ping + snnifing, iperf-tcp, (CPU), (iperf-udp)
        3. Depronto agregar cualquier otro ataque.
        """ 
        # Definiendo los traficos
        if e[1] == 'normal':
            trafico = TraficoNormal(C,V)
        elif e[1] == 'ataque':
            trafico = TraficoAtaque(A,C,V)
        net.start()
        print("Lanzando el experimeto espere 5s ...\n")
        sleep(5)
        print("Agregando las reglas al learning-switch mediante un pingall espere 1s...\n")        
        net.pingAll()
        sleep(1)
        # Llevando a cabo las respectivas mediciones (iperf, ping, etc.)
        
        


















