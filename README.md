# tp2-redes-openflow
Se propone desarrollar una topología parametrizable sobre la cual probaremos diferentes funcionalidades que nos brinda la tecnología OpenFlow. Se tendrá una cantidad de switches variable, formando una cadena, en cuyos extremos se tienen dos hosts. La topología debe recibir por parámetro la cantidad de switches.
- Prerequisitos:
    - Mininet
    - POX
    - Python 2.7
    - iperf

- Instalar Python 2.7 en Ubuntu:
    ```bash
        sudo add-apt-repository ppa:deadsnakes/ppa
        sudo apt-get update
        sudo apt-get install python2.7
    ```

- Correr pox en una terminal con Python 2.7:
    ```bash
    python2.7 pox.py log.level --DEBUG openflow.of_01 forwarding.l2_learning Firewall
    ```
    Usar el código de la rama fangtooth.

- Levantar la topología en otra terminal, especificando cantidad de switches deseada (> 0):
    ```bash
        sudo mn --custom topology.py --topo tp2,n_switches=[n] --arp --switch ovsk --controller remote
    ```
    
- Una vez lograda la topología, se debe verificar el correcto funcionamiento de la red mediante el comando pingall.
    
- Correr iperf en host: 
    Primero con xterm <nombre\_host> (dentro de mininet) abrimos dos terminales, es decir, para dos hosts. Luego ahí dentro, ejecutamos iperf:
    ```bash
        SERVIDOR: iperf -u -s -p [PUERTO]
        CLIENTE: iperf -u -c [IP SERVIDOR] -p [PUERTO SERVIDOR]
    ```
    Donde -u es para UDP, -c es cliente, -p es para especificar el puerto y -s es para servidor.

    De ser necesario correr iperf con TCP, se deben agregar limitaciones:
    ```bash
        iperf -c [IP SERVIDOR]  -p [PUERTO SERVIDOR] -b [x] -n [x] -l [x] -t [x]
    ```
    
    b - limita ancho de banda (ej 1Mb)
    
    n - limita cantidad de paquetes (ej 20)

    l - limita tamaño paquetes (ej 0 por ancho de banda)
    
    t - limita tiempo de conexion (ej 10 seg) 
