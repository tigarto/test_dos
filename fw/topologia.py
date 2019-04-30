from mininet.topo import Topo
from mininet.log import info, setLogLevel
from mininet.link import TCLink

class TopologiaRyu(Topo):
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

class TopologiaPOX(Topo):
    def __init__(self, bw = 100):
        # Initialize topology
        Topo.__init__(self)
        self.bw = bw
        h1 = self.addHost('h1', ip='10.0.0.1')  # Cliente
        h2 = self.addHost('h2', ip='10.0.0.2')  # Atacante
        h3 = self.addHost('h3', ip='10.0.0.3')  # Victima

        # Add switches
        info('*** Adding switches\n')
        s1 = self.addSwitch('s1')

        # Add links
        info('*** Creating links\n')
        self.addLink(h1, s1, bw = self.bw)
        self.addLink(h2, s1, bw = self.bw)
        self.addLink(h3, s1, bw = self.bw)

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