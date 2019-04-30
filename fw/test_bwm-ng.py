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

if __name__ == "__main__":
    setLogLevel( 'info' )
    # Creando la red: RYU + Single topo
    net = Mininet( topo=SingleSwitchTopo(k = 3), controller=RYU('c0'))
    # Obteniendo las interfaces de los switches
    net_sw = {}
    for k,v in net.items():
        if 's' in k:
            sw_int = []
            for i in range(1,len(v.ports)):
                sw_int.append(k + '-eth' + str(i))
            net_sw[k]=sw_int
            sw_int = []
    
    filename="monitoreo.csv"
    # Agrupando de insterfaces para pasar al comando bwm-ng
    list_interfaces = ''
    for k in net_sw:
        for int_sw in net_sw[k]:
            list_interfaces+=int_sw+','
    list_interfaces += 'lo' # Se agrega la interfaz localhost para verificar el trafico entre el
                            # switch y el controlador.
        
    
    """
    Lanzando el proceso asociado al comando
    """
    pid_hijo = os.fork()
    if pid_hijo == 0:
        # Proceso hijo
        comando = "bwm-ng -I " + \
                list_interfaces + \
                " -o csv -t 1000 > " + \
                filename

        info("%s\n"%(comando))
        os.system(comando)
    

    else:
        # Proceso padre
        info("Iniciando topologia mininet")
        net.start()
        CLI( net )
        net.stop()
        os.kill(pid_hijo,SIGKILL)


