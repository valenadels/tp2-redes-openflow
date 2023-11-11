from mininet.topo import Topo


class MyTopo(Topo):
    def __init__(self, n_switches):
        Topo.__init__(self)

        hosts = []
        for i in range(4):
            hosts.append(self.addHost('h'+str(i)))

        switches = []
        for i in range(n_switches):
            switches.append(self.addSwitch('s'+str(i)))

        self.addLink(hosts[0], switches[0])
        self.addLink(hosts[1], switches[0])
        self.addLink(hosts[2], switches[n_switches-1])
        self.addLink(hosts[3], switches[n_switches-1])

        for i in range(n_switches-1):
            self.addLink(switches[i], switches[i+1])


topos = {'mytopo': (lambda: MyTopo())}
