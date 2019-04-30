# Experimento #

```bash
sudo python disenoExperimental.py
```

## Problemas ##

1. El programa se bloquea cuando la conexión entre los host se queda abierta ya que el cliente que lleva a cabo la medición y la escritura del archivo se bloquea. Como posible solución se puede agregar una espera activa en un hilo en el programa principal de modo que se haga un kill del cliente del iperf para que se desbloque la ejecución del programa pero de momento no me ocurre nada mas.
2. Aun los archivos log no son definitivos

## Analisis por partes ##

### Controlador ###

El codigo asociado a esta clase se encuentra en el archivo [controlador.py](controlador.py)

#### Caso POX ####

```bash
sudo python controlador.py 
*** Ping: testing ping reachability
h1 -> h2 h3 h4 
h2 -> h1 h3 X 
h3 -> h1 X h4 
h4 -> h1 h2 h3 
*** Results: 16% dropped (10/12 received)
containernet> pingall
*** Ping: testing ping reachability
h1 -> h2 h3 h4 
h2 -> h1 h3 h4 
h3 -> h1 h2 h4 
h4 -> h1 h2 h3 
*** Results: 0% dropped (12/12 received)
containernet> 
```

**Observaciones**:
1. El primer pingAll dio imcompleto. Si se arrancara el controlador automaticamente por lo menos seria de utilidad dar dos pingall.

#### Caso RYU ####

```bash
sudo python controlador.py 
*** Ping: testing ping reachability
h1 -> h2 h3 h4 
h2 -> h1 h3 h4 
h3 -> h1 h2 h4 
h4 -> h1 h2 h3 
*** Results: 0% dropped (12/12 received)
containernet> pingall
*** Ping: testing ping reachability
h1 -> h2 h3 h4 
h2 -> h1 h3 h4 
h3 -> h1 h2 h4 
h4 -> h1 h2 h3 
*** Results: 0% dropped (12/12 received)
containernet>
```

**Observaciones**:
1. No presenta los mismos problemas que con POX con el primer pingAll, asi que al parecer es mas rapido para aprender.

### Unidad experimental ###

El codigo python [unidadExperimental.py](unidadExperimental.py) esta asociado a la clase que determina la unidad experimental. Para el caso la siguiente función python usa la clase alli definida para crear una unidad experimental con las siguientes caracteristicas:
1. Controlador ryu el cual corre la aplicación simple_switch_13.py.
2. Se emplea una topologia tree(2,2)
3. Se definen los nodos claves como h1,h2 y h3.

```python
# Parametros de la unidad experimental
info("Configurando unidad experimental\n")
setLogLevel("info")
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
```

A continuación se muestra la salida.

```bash
sudo python unidadExperimental.py 
Configurando e inicializando la red
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3 h4 
*** Adding switches:
s1 s2 s3 
*** Adding links:
(s1, s2) (s1, s3) (s2, h1) (s2, h2) (s3, h3) (s3, h4) 
*** Configuring hosts
h1 h2 h3 h4 
*** Starting controller
c0 
*** Starting 3 switches
s1 s2 s3 ...
*** Ping: testing ping reachability
h1 -> h2 h3 h4 
h2 -> h1 h3 h4 
h3 -> h1 h2 h4 
h4 -> h1 h2 h3 
*** Results: 0% dropped (12/12 received)
*** Starting CLI:
containernet> pingall
*** Ping: testing ping reachability
h1 -> h2 h3 h4 
h2 -> h1 h3 h4 
h3 -> h1 h2 h4 
h4 -> h1 h2 h3 
*** Results: 0% dropped (12/12 received)
```

Por otro lado se configura a continuacion otra unidad experimental donde se manejan los siguientes atributos:
1. Controlador POX el cual corre la aplicación forwarding.l2_learning_04.
2. Se emplea una topologia single con 4 hosts
3. Se definen los nodos claves como h1,h2 y h3.

El fragmento de codigo para hacer esto se muestra a continuación:

```python
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
```

La salida en mininet se muestra a continuación:

```bash
sudo python unidadExperimental.py 
Configurando unidad experimental
Configurando e inicializando la red
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3 h4 
*** Adding switches:
s1 
*** Adding links:
(h1, s1) (h2, s1) (h3, s1) (h4, s1) 
*** Configuring hosts
h1 h2 h3 h4 
*** Starting controller
c0 
*** Starting 1 switches
s1 ...
*** Ping: testing ping reachability
h1 -> h2 h3 h4 
h2 -> h1 h3 h4 
h3 -> h1 h2 h4 
h4 -> h1 h2 h3 
*** Results: 0% dropped (12/12 received)
*** Starting CLI:
containernet> net
h1 h1-eth0:s1-eth1
h2 h2-eth0:s1-eth2
h3 h3-eth0:s1-eth3
h4 h4-eth0:s1-eth4
s1 lo:  s1-eth1:h1-eth0 s1-eth2:h2-eth0 s1-eth3:h3-eth0 s1-eth4:h4-eth0
c0
containernet> 
```

### Trafico ###

El codigo python asociado al trafico es [trafico.py](trafico.py). 


A continuación se encuentra un fragmento con un ejemplo de uso:

```python
# Parametros de la unidad experimental
setLogLevel("info")
info("Configurando unidad experimental\n")
# 1. Definiendo la unidadexperimental
ue = UnidadExperimental(TreeTopo( depth=2, fanout=2 ),controller=RYU('c0'))
ue.definirNodosClaves('h1','h2','h3')
info("Configurando la red\n")
# 2. Configurando la red mininet a partir de la unidad experimental
net = Mininet(topo = ue.getTopo(),controller=ue.getController(),build=False)
net.build()
info("Configurando trafico normal\n")
[A,C,V] = ue.obtenerNodosClaves()
C = net.get(C)
V = net.get(V)
# 3. Configurando clase asociada al trafico   
t_normal = TraficoNormal(C,V)
info("Iniciando la red\n")
net.start()
info("Realizando pruebas en la red\n")
# 4. Llevando a cabo pruebas   
net.pingAllFull()
t_normal.pingMeasure() # Mostrando salida en pantalla
t_normal.pingMeasure(filename = 'ping_normal.log') # Llevando salida a un archivo
CLI(net)
info("Deteniendo la red red\n")
net.stop()
```

La salida en consola fue algo como lo siguiente:

```bash
# Comando python
sudo python trafico.py 

# Iniciando mininet
Configurando unidad experimental
Configurando la red
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3 h4 
*** Adding switches:
s1 s2 s3 
*** Adding links:
(s1, s2) (s1, s3) (s2, h1) (s2, h2) (s3, h3) (s3, h4) 
*** Configuring hosts
h1 h2 h3 h4 
Configurando trafico normal
Iniciando la red
*** Starting controller
c0 
*** Starting 3 switches
s1 s2 s3 ...
Realizando pruebas en la red
*** Ping: testing ping reachability
h1 -> h2 h3 h4 
h2 -> h1 h3 h4 
h3 -> h1 h2 h4 
h4 -> h1 h2 h3 
*** Results: 
 h1->h2: 1/1, rtt min/avg/max/mdev 2066.568/2066.568/2066.568/0.000 ms
 h1->h3: 1/1, rtt min/avg/max/mdev 9.961/9.961/9.961/0.000 ms
 h1->h4: 1/1, rtt min/avg/max/mdev 8.937/8.937/8.937/0.000 ms
 h2->h1: 1/1, rtt min/avg/max/mdev 0.097/0.097/0.097/0.000 ms
 h2->h3: 1/1, rtt min/avg/max/mdev 12.130/12.130/12.130/0.000 ms
 h2->h4: 1/1, rtt min/avg/max/mdev 9.072/9.072/9.072/0.000 ms
 h3->h1: 1/1, rtt min/avg/max/mdev 0.165/0.165/0.165/0.000 ms
 h3->h2: 1/1, rtt min/avg/max/mdev 0.070/0.070/0.070/0.000 ms
 h3->h4: 1/1, rtt min/avg/max/mdev 4.281/4.281/4.281/0.000 ms
 h4->h1: 1/1, rtt min/avg/max/mdev 0.117/0.117/0.117/0.000 ms
 h4->h2: 1/1, rtt min/avg/max/mdev 0.035/0.035/0.035/0.000 ms
 h4->h3: 1/1, rtt min/avg/max/mdev 0.021/0.021/0.021/0.000 ms
Starting Pings: 10.0.0.2 ---> 10.0.0.3
*** h2 : ('ping -c', 10, '-i', 1.0, '10.0.0.3')
PING 10.0.0.3 (10.0.0.3) 56(84) bytes of data.
64 bytes from 10.0.0.3: icmp_seq=1 ttl=64 time=0.039 ms
64 bytes from 10.0.0.3: icmp_seq=2 ttl=64 time=0.063 ms
64 bytes from 10.0.0.3: icmp_seq=3 ttl=64 time=0.071 ms
64 bytes from 10.0.0.3: icmp_seq=4 ttl=64 time=0.063 ms
64 bytes from 10.0.0.3: icmp_seq=5 ttl=64 time=0.061 ms
64 bytes from 10.0.0.3: icmp_seq=6 ttl=64 time=0.107 ms
64 bytes from 10.0.0.3: icmp_seq=7 ttl=64 time=0.107 ms
64 bytes from 10.0.0.3: icmp_seq=8 ttl=64 time=0.106 ms
64 bytes from 10.0.0.3: icmp_seq=9 ttl=64 time=0.087 ms
64 bytes from 10.0.0.3: icmp_seq=10 ttl=64 time=0.096 ms

--- 10.0.0.3 ping statistics ---
10 packets transmitted, 10 received, 0% packet loss, time 9203ms
rtt min/avg/max/mdev = 0.039/0.080/0.107/0.022 ms
End pings ***
Starting Pings: 10.0.0.2 ---> 10.0.0.3
Open file: ping_normal.log
End pings ***
*** Starting CLI:
containernet> 
```

El archivo resultante se muestra a continuación:

```
PING 10.0.0.3 (10.0.0.3) 56(84) bytes of data.
64 bytes from 10.0.0.3: icmp_seq=1 ttl=64 time=0.036 ms
64 bytes from 10.0.0.3: icmp_seq=2 ttl=64 time=0.077 ms
64 bytes from 10.0.0.3: icmp_seq=3 ttl=64 time=0.044 ms
64 bytes from 10.0.0.3: icmp_seq=4 ttl=64 time=0.074 ms
64 bytes from 10.0.0.3: icmp_seq=5 ttl=64 time=0.106 ms
64 bytes from 10.0.0.3: icmp_seq=6 ttl=64 time=0.084 ms
64 bytes from 10.0.0.3: icmp_seq=7 ttl=64 time=0.078 ms
64 bytes from 10.0.0.3: icmp_seq=8 ttl=64 time=0.092 ms
64 bytes from 10.0.0.3: icmp_seq=9 ttl=64 time=0.071 ms
64 bytes from 10.0.0.3: icmp_seq=10 ttl=64 time=0.065 ms

--- 10.0.0.3 ping statistics ---
10 packets transmitted, 10 received, 0% packet loss, time 9194ms
rtt min/avg/max/mdev = 0.036/0.072/0.106/0.022 ms
```

Lo que se midió anteiormente fue el ping.


<!---

```python
# ping
"""parte de mininet"""
result = node.cmd( 'ping -c1 %s %s' %
                                   (opts, manualdestip) )
                sent, received = self._parsePing( result )
                packets += sent
                if received > sent:
                    error( '*** Error: received too many packets' )
                    error( '%s' % result )
                    node.cmdPrint( 'route' )
                    exit( 1 )
                lost += sent - received

# iperf
server.sendCmd( iperfArgs + '-s' )

cliout = client.cmd( iperfArgs + '-t %d -c ' % seconds +
                             server.IP() + ' ' + bwArgs )
        debug( 'Client output: %s\n' % cliout )

        
    def iperf( self, hosts=None, l4Type='TCP', udpBw='10M', fmt=None,
               seconds=5, port=5001):
        """Run iperf between two hosts.
           hosts: list of hosts; if None, uses first and last hosts
           l4Type: string, one of [ TCP, UDP ]
           udpBw: bandwidth target for UDP test
           fmt: iperf format argument if any
           seconds: iperf time to transmit
           port: iperf port
           returns: two-element array of [ server, client ] speeds
           note: send() is buffered, so client rate can be much higher than
           the actual transmission rate; on an unloaded system, server
           rate should be much closer to the actual receive rate"""
        hosts = hosts or [ self.hosts[ 0 ], self.hosts[ -1 ] ]
        assert len( hosts ) == 2
        client, server = hosts
        output( '*** Iperf: testing', l4Type, 'bandwidth between',
                client, 'and', server, '\n' )
        server.cmd( 'killall -9 iperf' )
        iperfArgs = 'iperf -p %d ' % port
        bwArgs = ''
        if l4Type == 'UDP':
            iperfArgs += '-u '
            bwArgs = '-b ' + udpBw + ' '
        elif l4Type != 'TCP':
            raise Exception( 'Unexpected l4 type: %s' % l4Type )
        if fmt:
            iperfArgs += '-f %s ' % fmt
        server.sendCmd( iperfArgs + '-s' )
        if l4Type == 'TCP':
            if not waitListening( client, server.IP(), port ):
                raise Exception( 'Could not connect to iperf on port %d'
                                 % port )
        cliout = client.cmd( iperfArgs + '-t %d -c ' % seconds +
                             server.IP() + ' ' + bwArgs )
        debug( 'Client output: %s\n' % cliout )
        servout = ''
        # We want the last *b/sec from the iperf server output
        # for TCP, there are two fo them because of waitListening
        count = 2 if l4Type == 'TCP' else 1
        while len( re.findall( '/sec', servout ) ) < count:
            servout += server.monitor( timeoutms=5000 )
        server.sendInt()
        servout += server.waitOutput()
        debug( 'Server output: %s\n' % servout )
        result = [ self._parseIperf( servout ), self._parseIperf( cliout ) ]
        if l4Type == 'UDP':
            result.insert( 0, udpBw )
        output( '*** Results: %s\n' % result )
        return result

@staticmethod
    def _parseIperf( iperfOutput ):
        """Parse iperf output and return bandwidth.
           iperfOutput: string
           returns: result string"""
        r = r'([\d\.]+ \w+/sec)'
        m = re.findall( r, iperfOutput )
        if m:
            return m[-1]
        else:
            # was: raise Exception(...)
            error( 'could not parse iperf output: ' + iperfOutput )
            return ''
```
-->

## Referencias ##
1. https://www.bogotobogo.com/python/Multithread/python_multithreading_subclassing_Timer_Object.php
2. https://docs.python.org/2.4/lib/timer-objects.html
3. https://docs.python.org/3/library/sched.html
4. https://docs.python.org/2/library/sched.html
5. https://www.geeksforgeeks.org/timer-objects-python/
