#!/bin/sh -
# -*- coding: utf-8 -*-

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import IPAddr
import pox.lib.packet as pkt
import os
import json


log = core.getLogger()
policyFile = "%s/pox/pox/misc/firewall-policies.csv" % os.environ[ 'HOME' ]


class Firewall (EventMixin):
    def __init__ (self):
        self.listenTo(core.openflow)
        self.setConfiguration()
        log.debug("Enabling Firewall Module")

    def _handle_ConnectionUp (self, event):
        log.info("ConnectionUp for switch {}: ".format(event.dpid))
        if event.dpid == self.swith_id:  # Identificador del switch donde se instalarán las reglas
            self.setRules(event)

    def setConfiguration(self):
        file = open('config.json')
        config = json.load(file)
        file.close()
        self.swith_id = config["firewall_id"]
        self.rules = config["rules"]
    
    def setRules(self, event):
        # Regla 1: Descartar mensajes con puerto destino 80
        rule1_udp = of.ofp_flow_mod()
        rule1_udp.match.tp_dst = self.rules[0]["dst_port"]  # Puerto destino 80
        rule1_udp.match.dl_type = pkt.ethernet.IP_TYPE
        rule1_udp.match.nw_proto = pkt.ipv4.UDP_PROTOCOL
        event.connection.send(rule1_udp)

        rule1_tcp = of.ofp_flow_mod()
        rule1_tcp.match.tp_dst = self.rules[0]["dst_port"]  # Puerto destino 80
        rule1_tcp.match.dl_type = self.typeIp(self.rules[0]["ip_type"])
        rule1_tcp.match.nw_proto = pkt.ipv4.TCP_PROTOCOL
        event.connection.send(rule1_tcp)
        
        # Regla 2: Descartar mensajes desde el host 1 al puerto 5001 usando UDP
        rule2 = of.ofp_flow_mod()
        rule2.match.dl_type = pkt.ethernet.IP_TYPE
        if self.rules[1]["protocol"] == "UDP":
            rule2.match.nw_proto = pkt.ipv4.UDP_PROTOCOL
        elif self.rules[1]["protocol"] == "TCP":
            rule2.match.nw_proto = pkt.ipv4.TCP_PROTOCOL
        rule2.match.nw_src = IPAddr(self.rules[1]["src_ip"])  # Dirección IP del host 1
        rule2.match.tp_dst = self.rules[1]["dst_port"]  # Puerto destino 5001
        event.connection.send(rule2)

        # Regla 3: Bloqueo de comunicacion entre 2 hosts cualquiera (bilateral).
        rule3_1 = of.ofp_flow_mod()
        rule3_1.match.dl_type = pkt.ethernet.IP_TYPE
        rule3_1.match.nw_src = IPAddr(self.rules[2]["src_ip"])
        rule3_1.match.nw_dst = IPAddr(self.rules[2]["dst_ip"])
        event.connection.send(rule3_1)
        
        rule3_2 = of.ofp_flow_mod()
        rule3_2.match.dl_type = pkt.ethernet.IP_TYPE
        rule3_2.match.nw_src = IPAddr(self.rules[2]["dst_ip"])
        rule3_2.match.nw_dst = IPAddr(self.rules[2]["src_ip"])
        event.connection.send(rule3_2)

        log.debug("FIREWALL RULES INSTALLED ON SWITCH %s", dpidToStr(event.dpid))

    def typeIp(self, type):
        if type == "ipv4":
            return pkt.ethernet.IP_TYPE
        elif type == "ipv6":
            return  pkt.ethernet.IPV6_TYPE

def launch():
    core.registerNew(Firewall)