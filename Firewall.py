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

    def setRules(self, event):
        '''
        for rule in self.rules:
            flow_mod = self.create_flow_mod(rule)
            event.connection.send(flow_mod)
        '''
        # Regla 1: Descartar mensajes con puerto destino 80
        rule1_udp = of.ofp_flow_mod()
        rule1_udp.match.tp_dst = self.rules[0]["dst_port"]  # Puerto destino 80
        rule1_udp.match.dl_type = self.mapIpType(self.rules[0]["ip_type"])
        rule1_udp.match.nw_proto = pkt.ipv4.UDP_PROTOCOL
        event.connection.send(rule1_udp)

        rule1_tcp = of.ofp_flow_mod()
        rule1_tcp.match.tp_dst = self.rules[0]["dst_port"]  # Puerto destino 80
        rule1_tcp.match.dl_type = self.mapIpType(self.rules[0]["ip_type"])
        rule1_tcp.match.nw_proto = pkt.ipv4.TCP_PROTOCOL
        event.connection.send(rule1_tcp)

        # Regla 2: Descartar mensajes desde el host 1 al puerto 5001 usando UDP
        rule2 = of.ofp_flow_mod()
        rule2.match.dl_type = self.mapIpType(self.rules[1]["ip_type"])
        if self.rules[1]["protocol"] == "UDP":
            rule2.match.nw_proto = pkt.ipv4.UDP_PROTOCOL
        elif self.rules[1]["protocol"] == "TCP":
            rule2.match.nw_proto = pkt.ipv4.TCP_PROTOCOL
        rule2.match.nw_src = IPAddr(self.rules[1]["src_ip"])  # Dirección IP del host 1
        rule2.match.tp_dst = self.rules[1]["dst_port"]  # Puerto destino 5001
        event.connection.send(rule2)

        # Regla 3: Bloqueo de comunicacion entre 2 hosts cualquiera (bilateral).
        rule3_1 = of.ofp_flow_mod()
        rule3_1.match.dl_type = self.mapIpType(self.rules[2]["ip_type"])
        rule3_1.match.nw_src = IPAddr(self.rules[2]["src_ip"])
        rule3_1.match.nw_dst = IPAddr(self.rules[2]["dst_ip"])
        event.connection.send(rule3_1)

        rule3_2 = of.ofp_flow_mod()
        rule3_2.match.dl_type = self.mapIpType(self.rules[2]["ip_type"])
        rule3_2.match.nw_src = IPAddr(self.rules[2]["dst_ip"])
        rule3_2.match.nw_dst = IPAddr(self.rules[2]["src_ip"])
        event.connection.send(rule3_2)

        log.debug("FIREWALL RULES INSTALLED ON SWITCH %s", dpidToStr(event.dpid))

    def create_flow_mod(self, rule):
        flow_mod = of.ofp_flow_mod()
        flow_mod.match.dl_type = self.mapIpType(rule["ip_type"])

        if "src_ip" in rule:
            flow_mod.match.nw_src = IPAddr(rule["src_ip"])
        if "dst_ip" in rule:
            flow_mod.match.nw_dst = IPAddr(rule["dst_ip"])
        if "src_port" in rule:
            flow_mod.match.tp_src = rule["src_port"]
        if "dst_port" in rule:
            flow_mod.match.tp_dst = rule["dst_port"]
        if "protocol" in rule:
            if rule["protocol"] == "UDP":
                flow_mod.match.nw_proto = pkt.ipv4.UDP_PROTOCOL
            elif rule["protocol"] == "TCP":
                flow_mod.match.nw_proto = pkt.ipv4.TCP_PROTOCOL

        return flow_mod


    def mapIpType(self, type):
        if type == "ipv6":
            return  pkt.ethernet.IPV6_TYPE
        return pkt.ethernet.IP_TYPE


    def setConfiguration(self):
        file = open('config.json')
        config = json.load(file)
        file.close()
        self.swith_id = config["firewall_id"]
        self.rules = config["rules"]
    
def launch():
    core.registerNew(Firewall)