from mininet.topo import Topo

MAX_HOSTS = 4
MIN_SWITCHES = 1
HOST = 'h'
SWITCH = 's'

class Tp2Topo(Topo):
    def __init__(self, n_switches):
        Topo.__init__(self)
        if n_switches < MIN_SWITCHES:
            raise Exception("Number of switches must be at least 1")
        

        hosts = []
        for i in range(MAX_HOSTS):
            hosts.append(self.addHost(HOST+str(i + 1)))

        switches = []
        for i in range(n_switches):
            switches.append(self.addSwitch(SWITCH+str(i+1)))

        self.addLink(hosts[0], switches[0])
        self.addLink(hosts[1], switches[0])
        self.addLink(hosts[2], switches[n_switches-1])
        self.addLink(hosts[3], switches[n_switches-1])

        for i in range(n_switches-1):
            print("connect switch {} with {}".format(i+1, i+2))
            self.addLink(switches[i], switches[i+1])


topos = {'tp2': Tp2Topo}