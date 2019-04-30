#!/usr/bin/python

from mininet.log import setLogLevel, info
from mininet.net import Mininet
from mininet.topolib import TreeTopo
from mininet.cli import CLI
from mininet.topo import SingleSwitchTopo
from signal import SIGKILL
# We assume you are in the same directory as pox.py
# or that it is loadable via PYTHONPATH
from controlador import RYU,POX
import os
import subprocess
import time

# Solucion tomada de http://csie.nqu.edu.tw/smallko/sdn/openflow_pkts.htm



if __name__ == "__main__":
    setLogLevel( 'info' )
    # Creando la red: RYU + Single topo
    net = Mininet( topo=SingleSwitchTopo(k = 3), controller=RYU('c0'),build=False)
    # Obteniendo las interfaces de los switches  
    """
    Lanzando el proceso asociado al comando
    """
    
    # Proceso padre
    info("Iniciando topologia mininet")
    net.build()    
    net.start()
    net.getNodeByName('c0').cmd("tcpdump -i any -nn port 6653 -U -w mylog &")
    time.sleep(3)
    CLI( net )
    net.stop()
    net.getNodeByName('c0').cmd("pkill tcpdump")

    """
        info("Iniciando topologia mininet")
        net.start()
        CLI( net )
        net.stop()
        os.kill(pid_hijo,SIGKILL)
    """

# hping3 --flood --rand-source 10.0.0.3

# tshark -d tcp.port==6633,openflow -r mylog