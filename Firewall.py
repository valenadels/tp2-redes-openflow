#!/bin/sh -
# -*- coding: utf-8 -*-

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
from collections import namedtuple
import os
import json
''' Add your imports here ... '''



log = core.getLogger()
policyFile = "%s/pox/pox/misc/firewall-policies.csv" % os.environ[ 'HOME' ]

''' 
En POX, que es un controlador de redes definidas por software (SDN) basado en OpenFlow, ofp_flow_mod es un mensaje OpenFlow utilizado para modificar o agregar flujos en un switch.
La estructura ofp_flow_mod se utiliza para especificar las reglas que determinan cómo se deben procesar los paquetes en el switch. Algunos de los parámetros importantes que se pueden incluir en un mensaje ofp_flow_mod son:

* match: Especifica las condiciones que deben cumplir los paquetes para que la regla se aplique. Puede incluir criterios como direcciones MAC, direcciones IP, puertos, etc.
* actions: Indica las acciones que deben realizarse cuando un paquete coincide con las condiciones especificadas en el campo match. Puede incluir acciones como reenviar a un puerto específico, modificar campos del encabezado del paquete, descartar el paquete, etc.
'''

"""
Prerequisitos:
- 1st -> SET IP MATCH: IPV4 or IPV6
- 2nd -> SET TRANSPORT MATCH: TCP or UDP
- 3rd -> SET PORT or DIR MATCH
"""

class Firewall (EventMixin):

    def __init__ (self):
        self.listenTo(core.openflow)
        self.setConfiguration()
        log.debug("Enabling Firewall Module")

    def _handle_ConnectionUp (self, event):
        """
        if event.dpid == 1:  # Identificador del switch
            # Regla 1: Descartar mensajes desde el host 1 al puerto 5001 usando UDP
            #msg1 = of.ofp_flow_mod()
            # msg1.match.dl_type = 0x800  # IPv4

            #msg1.match.tp_dst = 5001  # Puerto destino 5001
            #msg1.match.nw_proto = 17  # Protocolo UDP
            #event.connection.send(msg1)

            # Regla 2: Bloquear la comunicación entre dos hosts específicos
            msg2 = of.ofp_flow_mod()
            msg2.match.nw_src = self.rules[1]["src_ip"]  # Dirección IP del host 1
            msg2.match.dl_type = 0x800
            if self.rules[1]["protocol"] == "UDP":
                msg2.match.nw_proto = 17 # UDP ["protocol"] number
            elif self.rules[1]["protocol"] == "TCP":
                msg2.match.nw_proto = 6 # TCP protocol number
            msg2.match.tp_dst = self.rules[1]["dst_port"]  # Puerto destino 5001
            event.connection.send(msg2)

            # Regla 3: Bloquear la comunicación entre dos hosts específicos
            #msg3 = of.ofp_flow_mod()
            #msg3.match = of.ofp_match(dl_src="00:00:00:00:00:01", dl_dst="00:00:00:00:00:02") 
            #msg3.actions.append(of.ofp_action_output(port=of.OFPP_NONE)) 

            # Enviar el mensaje al switch
            #event.connection.send(msg3)
        """
        log.debug("Firewall rules installed on %s", dpidToStr(event.dpid))

    def setConfiguration(self):
        file = open('config.json')
        config = json.load(file)
        file.close()
        self.swith_id = config["firewall_id"]
        self.rules = config["rules"]

def launch():
    core.registerNew(Firewall)