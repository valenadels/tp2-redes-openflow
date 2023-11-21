# tp2-redes-openflow
Se propone desarrollar una topología parametrizable sobre la cual probaremos diferentes funcionalidades que nos brinda la tecnología OpenFlow. Se tendrá una cantidad de switches variable, formando una cadena, en cuyos extremos se tienen dos hosts. La topología debe recibir por parámetro la cantidad de switches.
- Prerequisitos:
    - Mininet
    - POX
    - Python 2.7
    - iperf
- Correr pox en una terminal con Python 2:
    ```bash
    python2.7 pox.py log.level --DEBUG openflow.of_01 forwarding.l2_learning Firewall
    ```
    Usar el código de la rama fangtooth.

- Levantar la topología en otra terminal, especificando cantidad de switches deseada (> 0):
    ```bash
        sudo mn --custom topology.py --topo tp2,n_switches=4 --controller remote
    ```
    
- Una vez lograda la topología, se debe verificar el correcto funcionamiento de la red mediante el comando pingall.
    
- Correr iperf en host: 
    Primero con xterm <nombre\_host> (dentro de mininet) abrimos dos terminales, es decir, para dos hosts. Luego ahí dentro, ejecutamos iperf:
    ```bash
        SERVIDOR (usando host1): iperf -u -s -p 80
        CLIENTE (cualquier host): iperf -u -c 10.0.0.2 -p 80
    ```

    De ser necesario correr iperf con TCP, se deben agregar limitaciones:
    ```bash
        iperf -c 10.0.0.1 -p 80 -b 1 -n 20 -l 0 -t 10
    ```
    
    b - limita ancho de banda (1Mb)
    
    n - limita cantidad de paquetes (20)

    l - limita tamaño paquetes (0 por ancho de banda)
    
    t - limita tiempo de conexion (10 seg) 
