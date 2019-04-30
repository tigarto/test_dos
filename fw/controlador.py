import os
from mininet.net import Mininet
from mininet.log import info, setLogLevel
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.link import TCLink
from mininet.topo import Topo
import subprocess
from time import time, sleep
import psutil
from mininet.cli import CLI
from subprocess import Popen, PIPE, STDOUT
from select import poll, POLLIN
from os import environ
from mininet.topolib import TreeTopo 

class RYU( Controller ):

    """
    Clase usada para representar un controlador Ryu

    ...

    Attributes
    ----------
    None

    Methods
    -------
    None        
    """


    def __init__(self, name, ryuArgs = 'simple_switch_13.py', **kwargs):
        """
        Parameters
        ----------
        name : str
            Nombre del controlador en la topologia
        ryuArgs : str
            Aplicacion que ejecutara el controlador
        """
        Controller.__init__(self, name,
                            command = '/usr/local/bin/ryu-manager',
                            cargs='--ofp-tcp-listen-port %s ' + ryuArgs,
                            **kwargs)

POXDIR = environ[ 'HOME' ] + '/pox-1.3'

class POX( Controller ):
    """
    Clase usada para representar un controlador POX

    ...

    Attributes
    ----------
    None

    Methods
    -------
    None        
    """

    def __init__( self, name, cdir=POXDIR,
                  command='python pox.py',
                  poxArgs = 'forwarding.l2_learning_04',
                  **kwargs ):
        """
        Parameters
        ----------
        name : str
            Nombre del controlador en la topologia
        cdir : str
            Directorio donde se encuentran las aplicaciones de POX
        command : str
            Comando de invocacion del controlador
        poxArgs : str
            Aplicaciones que se ejecutaran en el controlador
        """
        if poxArgs == None:
            poxArgs = 'forwarding.l2_learning_04'
        cargs = 'openflow.of_04 --port=%s ' + poxArgs
        Controller.__init__( self, name, cdir=cdir,
                             command=command,
                             cargs=cargs, **kwargs )

"""
Codigo test
"""

def testPOX():
    net = Mininet( topo=TreeTopo( depth=2, fanout=2 ),
                   controller=POX('c0') )                  
    net.start()
    net.pingAll()
    CLI( net )
    net.stop()

def testRYU():
    net = Mininet( topo=TreeTopo( depth=2, fanout=2 ),
                   controller=RYU('c0') )               
    net.start()
    net.pingAll()
    CLI( net )
    net.stop()

if __name__ == "__main__":
    # testPOX()
    testRYU()