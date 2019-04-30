import os
from mininet.net import Mininet
from mininet.log import info, setLogLevel
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.link import TCLink
import subprocess
from time import time, sleep
import psutil
from mininet.cli import CLI
from mininet.topo import Topo


from trafico import TraficoAtaque, TraficoNormal
from unidadExperimental import UnidadExperimental
from controlador import RYU, POX
import subprocess


class Experimento:

    """
    Clase usada para representar un experimento

    ...

    Attributes
    ----------
    net
    inputs
    trafico

    Methods
    -------
    configureParams
    getUnidadExperimental
    configurarTrafico
    killTest
    killController
    startTest
    endTest
    startCLI
    pingAllTest        
    """

    def __init__(self):
        self.net = None
        self.inputs = None
        self.trafico = None

    def configureParams(self,ue):
        self.inputs = ue
        self.net = Mininet( controller=ue.getController(),
                            switch=OVSSwitch,
                            build=False,
                            link=TCLink,
                            topo = ue.getTopo()
                          )
        sleep(5) # Dando un tiempo de espera para que el controlador arranque
        self.net.build()

    # Metodo para configurar la unidad experimental
    def getUnidadExperimental(self):
        return self.inputs

    # Metodo para configurar el trafico
    def configurarTrafico(self, tipo = 'normal'):
        nodos_claves = self.inputs.obtenerNodosClaves()
        if tipo == 'normal':
            h_c = self.net.get(nodos_claves[1])
            h_v = self.net.get(nodos_claves[2])
            self.trafico = TraficoNormal(h_c,h_v)
        elif tipo == 'ataque':
            h_a = self.net.get(nodos_claves[0])
            h_c = self.net.get(nodos_claves[1])
            h_v = self.net.get(nodos_claves[2])
            self.trafico = TraficoAtaque(h_a,h_c,h_v)


    def killTest(self):
        subprocess.call(["mn", "-c"])

    def killController(self,port = 6653):
        subprocess.Popen(['sudo','fuser','-k',str(port)+'/tcp'])
                
    def startTest(self):
        self.net.start()

    def endTest(self):
        self.net.stop()

    def startCLI(self):
        CLI(self.net)

    def pingAllTest(self):
        self.net.pingAll()

## Funciones de test ##


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

ue_ryu = UnidadExperimental(topo=TopologiaTest(100),controller=RYU('c0'))
ue_ryu.definirNodosClaves('h1','h2','h3')

ue_pox = UnidadExperimental(topo=TopologiaTest(100),controller=POX('c0'))
ue_pox.definirNodosClaves('h1','h2','h3')

def test_cli(ue,nombreArchivo = None):
    # Parametros de la unidad experimental
    setLogLevel("info")
    info("Configurando unidad experimental\n")
    info("Configurando trafico normal\n")
    info("Configurando la red\n")
    net = Mininet(topo = ue.getTopo(),controller=ue.getController(),build=False)
    print ("Configuracion del experimento")
    experimento = Experimento()
    experimento.configureParams(ue)
    experimento.configurarTrafico()  # Se deduce de la unidad experimental
    print ("Realizacion de las pruebas")
    experimento.startTest()
    experimento.startCLI()
    experimento.endTest()
    print ("Removiendo la topologia")
    experimento.killTest()
    print ("Removiendo el controlador")
    experimento.killController()   # Si no se pone no se finaliza el controlador


def test_ping_normal(ue,nombreArchivo = None):
    # Parametros de la unidad experimental
    setLogLevel("info")
    info("Configurando unidad experimental\n")
    info("Configurando trafico normal\n")
    info("Configurando la red\n")
    print ("Configuracion del experimento")
    experimento = Experimento()
    experimento.configureParams(ue)
    experimento.configurarTrafico(tipo='normal')  # Se deduce de la unidad experimental
    # Arrancando la red para dar inicio a las pruebas
    experimento.startTest()
    # Llevando a cabo las pruebas
    experimento.net.pingAll() # Se lleva a cabo esto para que el controlador aprenda la red
    sleep(5) # Dando un tiempo prudencial antes de la siguiente prueba
    experimento.trafico.pingMeasure(filename=nombreArchivo)    # Finalizando las pruebas
    experimento.endTest()
    experimento.killTest()
    experimento.killController()

def test_iperf_normal(ue,nombreArchivo = None):
    # Parametros de la unidad experimental
    setLogLevel("info")
    info("Configurando unidad experimental\n")
    info("Configurando trafico normal\n")
    info("Configurando la red\n")
    print ("Configuracion del experimento")
    experimento = Experimento()
    experimento.configureParams(ue)
    experimento.configurarTrafico(tipo='normal')  # Se deduce de la unidad experimental
    # Arrancando la red para dar inicio a las pruebas
    experimento.startTest()
    # Llevando a cabo las pruebas
    experimento.net.pingAll() # Se lleva a cabo esto para que el controlador aprenda la red
    sleep(5) # Dando un tiempo prudencial antes de la siguiente prueba
    experimento.trafico.iperfMeasure(filename=nombreArchivo)    # Finalizando las pruebas
    experimento.endTest()
    experimento.killTest()
    experimento.killController()


if __name__ == "__main__":
    ## Testing CLI ##
    # test_cli(ue_ryu) # CLI usando ryu -> OK
    # test_cli(ue_pox) # CLI usando pox -> 
    # test_ping_normal(ue_ryu,'ping_normal_ryu.log') # Medicion del ping para trafico normal en ryu-> OK
    # test_ping_normal(ue_pox,'ping_normal_pox.log') # Medicion del ping para trafico normal en pox -> OK
    test_iperf_normal(ue_ryu,'iperf_normal_ryu.log') # Medicion del iperf para trafico normal en ryu -> OK
    # test1()    # OK
    # test2()    # OK
    # test3()    # Prueba con ping normal (consola y archivo) - OK
    #test4()    # Prueba con iperf normal (consola y archivo) - OK ** No se ve la cosa en pantalla
    # test5()    # Prueba con ping bajo ataque - Parece que OK
    # test6()      # Prueba con iperf bajo ataque (consola y archivo parece que OK) - Nota: Solo hacer un caso pues el
                 # resultado se afecta.
    # test7()
