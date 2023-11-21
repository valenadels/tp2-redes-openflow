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
        for rule in self.rules["rules"]:
            flow_mod = self.create_flow_mod(rule)
            event.connection.send(flow_mod)

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