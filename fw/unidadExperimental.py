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
from controlador import RYU, POX
from mininet.topolib import TreeTopo 

class UnidadExperimental:

    """
    Clase que define la unidad experimental

    ...

    Attributes
    ----------
    name : Topo
        Topologia a evaluar
    controller : RYU o POX
        Controlador a usar
    atacante : str
        Nodo de la topologia que sera empleado como atacante    
    cliente : str
        Nodo de la topologia que sera empleado como cliente
    victima : str
        Nodo de la topologia que sera empleado como victima

    Methods
    -------
    setTopo(topo)
        Asigna la topologia al experimento
    setController(controller, appsController)
        Asigna el controlador (RYU o POX) y la aplicacion que este correra en la unidad experimental. 
    getTopo()
        Obtiene la topologia asociada a la unidad experimental
    getController()
        Obtiene el controlador a la unidad experimental
    definirNodosClaves(A = None,C = None ,V = None)
        Defina los nodos de la topologia (h_i) que seran atacante (A), cliente (C) y victima (V)
    obtenerNodosClaves()
        Obtiene los nodos clave (atacante, cliente y servidor)
    """


    def __init__(self, topo = None, controller = None):
        """
        Parameters
        ----------
        topo : Topo
            Topologia para la unidad experimental
        controller : RYU o POX
            Controlador de la unidad experimental
        """
        self.topo = topo
        self.controller = controller
        self.atacante = None
        self.victima = None
        self.cliente = None

    def setTopo(self,topo):
        """
        Asigna la topologia a la unidad experimental.

        Parameters
        ----------
        topo: Topo
            La topologia a emplear

        Returns
        -------
        None

        Raises
        ------
        No hay manejo de errores
        """
        self.topo = topo

    # Puede que sea necesario revisarlo
    def setController(self,controller,appsController):
        """
        Asigna el controlador a la unidad experimental.

        Parameters
        ----------
        controller: str
            nombre del controlador a usar
        
        Returns
        -------
        None

        Raises
        ------
        No hay manejo de errores
        """
        if controller == 'ryu':
            self.controller = RYU(name='c0',
                                  ryuArgs =appsController)
        else:
            self.controller = POX(name = 'c0') # Mejorar ---------------

    def getTopo(self):
        """
        Retorna la topologia empleada en la unidad experimental

        Parameters
        ----------
        None

        Returns
        -------
        Topo
            Topologia asignada en la unidad experimental
        """
        return self.topo

    def getController(self):
        """
        Retorna el controlador empleada en la unidad experimental

        Parameters
        ----------
        None

        Returns
        -------
        Controladores RYU o POX
            Controlador empleado en la unidad experimental
        """
        return self.controller

    def definirNodosClaves(self,A = None,C = None ,V = None):
        """
        Asigna los nodos atacante, cliente y victima de la unidad experimental.

        Parameters
        ----------
        A: str
            Nombre del nodo atacante
        C: str
            Nombre del nodo cliente
        V: str
            Nombre del nodo victima
        
        Returns
        -------
        None

        Raises
        ------
        No hay manejo de errores
        """
        self.atacante = A
        self.cliente = C
        self.victima = V

    def obtenerNodosClaves(self):
        """
        Retorna los nodos atacante, cliente y victima de la unidad experimental.

        Parameters
        ----------
        None
        
        Returns
        -------
        Los nodos atacante, victima y cliente configurados en la unidad experimental

        Raises
        ------
        No hay manejo de errores
        """
        return [self.atacante, self.cliente, self.victima]

def test_ue1():
    # Parametros de la unidad experimental
    setLogLevel("info")
    info("Configurando unidad experimental\n")
    c_ryu = RYU('c0')
    topo_tree = TreeTopo( depth=2, fanout=2 )
    ue1 = UnidadExperimental(topo=topo_tree,controller=c_ryu)
    ue1.definirNodosClaves('h1','h2','h3')
    # Iniciando mininet a partir de la unidad experimental
    info("Configurando e inicializando la red\n")
    net = Mininet( topo=ue1.getTopo(), controller=ue1.getController())
    net.start()
    net.pingAll()
    CLI( net )
    net.stop()

def test_ue2():
    # Parametros de la unidad experimental
    setLogLevel("info")
    info("Configurando unidad experimental\n")
    ue2 = UnidadExperimental(topo=SingleSwitchTopo(k = 4),controller=POX('c0'))
    ue2.definirNodosClaves('h1','h2','h3')
    # Iniciando mininet a partir de la unidad experimental
    info("Configurando e inicializando la red\n")
    net = Mininet( topo=ue2.getTopo(), controller=ue2.getController())
    net.start()
    net.pingAll()
    CLI( net )
    net.stop()


if __name__ == "__main__":
    # test_ue1()
    test_ue2()