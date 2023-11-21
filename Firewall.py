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
        if event.dpid == self.swith_id: # Identificador del switch donde se instalarán las reglas
            self.setRules(event)

    def setRules(self, event):
        # Regla 1: Descartar mensajes con puerto destino 80
        self.portRule(pkt.ipv4.UDP_PROTOCOL)
        self.portRule(pkt.ipv4.TCP_PROTOCOL)

        # Regla 2: Descartar mensajes desde el host 1 al puerto 5001 usando UDP
        rule2 = of.ofp_flow_mod()
        rule2.match.dl_type = self.mapIpType(self.rules[1]["ip_type"])
        rule2.match.nw_proto = self.mapTransportProtocol(self.rules[1]["protocol"])
        rule2.match.nw_src = IPAddr(self.rules[1]["src_ip"])  # Dirección IP del host 1
        rule2.match.tp_dst = self.rules[1]["dst_port"]  # Puerto destino 5001
        event.connection.send(rule2)

        # Regla 3: Bloqueo de comunicacion entre 2 hosts cualquiera (bilateral).
        self.hostRule(event, self.rules[2]["src_ip"], self.rules[2]["dst_ip"])
        self.hostRule(event, self.rules[2]["dst_ip"], self.rules[2]["src_ip"])

        log.info("FIREWALL RULES INSTALLED ON SWITCH %s", dpidToStr(event.dpid))

    def portRule(self, event, transport_protocol):
        rule = of.ofp_flow_mod()
        rule.match.tp_dst = self.rules[0]["dst_port"]  # Puerto destino 80
        rule.match.dl_type = self.mapIpType(self.rules[0]["ip_type"])
        rule.match.nw_proto = transport_protocol
        event.connection.send(rule)

    def hostRule(self, event, nw_src, nw_dst):
        rule = of.ofp_flow_mod()
        rule.match.dl_type = self.mapIpType(self.rules[2]["ip_type"])
        rule.match.nw_src = IPAddr(nw_src)
        rule.match.nw_dst = IPAddr(nw_dst)
        event.connection.send(rule)
    
    def mapIpType(self, type):
        if type == "ipv6":
            return  pkt.ethernet.IPV6_TYPE
        return pkt.ethernet.IP_TYPE
    
    def mapTransportProtocol(self, protocol):
        if protocol == "UDP":
            return pkt.ipv4.UDP_PROTOCOL
        return pkt.ipv4.TCP_PROTOCOL

    def setConfiguration(self):
        file = open('config.json')
        config = json.load(file)
        file.close()
        self.swith_id = config["firewall_id"]
        self.rules = config["rules"]

    
def launch():
    core.registerNew(Firewall)