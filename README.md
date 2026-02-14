# DHCP Starvation Attack Tool

## Descripción

Este es un script que puede ser utilizado como herramienta con fines educativos para realizar ataques de DHCP Starvation en entornos de laboratorio, utilizando la herramienta Scapy para llevarlos a cabo. Este script envía paquetes DHCP DISCOVER con MACs aleatorias para agotar el pool de IPs del servidor DHCP.

## Objetivo del script

Demostrar vulnerabilidades DHCP llevando a cabo lo siguiente:

- Agotando todas las IPs disponibles en el pool DHCP.
- Impidiendo que clientes legítimos obtengan direcciones IP.
- Causando denegación de servicio (DoS) en la red.

## Topología

<img width="673" height="609" alt="image" src="https://github.com/user-attachments/assets/ce61e4f5-3eb4-487e-a83b-ed567a9d1b30" />

## Configuración dispositivos principales

| Dispositivo | Interfaz | IP | VLAN | Rol |
|------------|----------|-----|------|-----|
| Router (DHCP) | F0/0.20 | 20.24.11.129/26 | 20 | Servidor DHCP |
| Atacante (Kali) | Eth1 | 20.24.11.130/26 | 20 | Host con Scapy |
| Víctima | Eth0 | - | 20 | DHCP Client |

### Configuración del Router

```cisco
hostname R1
!
int f0/0.10
encapsulation dot1q 10
ip address 20.24.11.65 255.255.255.192
ip helper-address 20.24.11.65
!
int f0/0.20
encapsulation dot1q 20
ip address 20.24.11.129 255.255.255.192
ip helper-address 20.24.11.129
!
int f0/0.99
encapsulation dot1q 99
ip address 20.24.11.1 255.255.255.192
!
int f0/0.88
encapsulation dot1q 88 native
!
ip dhcp excluded-address 20.24.11.65
ip dhcp excluded-address 20.24.11.127
ip dhcp pool VLAN10
network 20.24.11.64 255.255.255.192
default-router 20.24.11.65
dns-server 8.8.8.8
!
ip dhcp excluded-address 20.24.11.129
ip dhcp excluded-address 20.24.11.191
ip dhcp pool VLAN20
network 20.24.11.128 255.255.255.192
default-router 20.24.11.129
dns-server 8.8.8.8
```

### Configuración del Switch 1

```cisco
hostname SW1
!
vlan 99
name Administration
vlan 10
name Operations
vlan 20
name Users
vlan 999
name ParkingLot
vlan 88
name Native
!
int vlan 99
ip add 20.24.11.59 255.255.255.0
no shutdown
ip default-gateway 20.24.11.1
!
int e0/0
sw trunk encapsulation dot1q
sw mode trunk
sw trunk native vlan 88
no shutdown
!
int range e0/1-2
sw trunk encapsulation dot1q
sw mode trunk
sw trunk native vlan 88
no shutdown
```

### Configuración del Switch 2

```cisco
hostname SW2
!
vlan 99
name Administration
vlan 10
name Operations
vlan 20
name Users
vlan 999
name ParkingLot
vlan 88
name Native
!
int vlan 99
ip add 20.24.11.10 255.255.255.0
no shutdown
ip default-gateway 20.24.11.1
!
int range e0/1-2
sw trunk encapsulation dot1q
sw mode trunk
sw trunk native vlan 88
no shutdown
!
int e0/3
sw mode access
sw access vlan 20
no shutdown
exit
```

### Configuración del Switch 3

```cisco
hostname SW3
!
vlan 99
name Administration
vlan 10
name Operations
vlan 20
name Users
vlan 999
name ParkingLot
vlan 88
name Native
!
int vlan 99
ip add 20.24.11.20 255.255.255.0
no shutdown
ip default-gateway 20.24.11.1
!
int range e0/0-1
sw trunk encapsulation dot1q
sw mode trunk
sw trunk native vlan 88
no shutdown
!
int e0/2
sw mode access
sw access vlan 20
no shutdown
```

## Requisitos para utilizar la herramienta

### Software

- Python 3.8+
- Scapy 2.5.0+
- GNS3 2.2+
- VM Linux

### Instalación y uso de herramienta Scapy

```bash
# Instalar Scapy
sudo pip3 install scapy

# Verificar
python3 -c "from scapy.all import *"

# Identificar interfaz
ip a

# Ejecución básica
sudo python3 Scapy_dhcp_starvation.py
```

Permisos: Requiere root/sudo para envío de paquetes raw en capa 2.

### Personalización del script

```python
interfaz_objetivo = "eth1" # Interfaz de red
# time.sleep(0.001) # Velocidad (comentado = máxima)
if packet_count % 100 == 0: # Frecuencia de reportes
```

### Comandos para verificar

```bash
# Ver pool agotado
Router# show ip dhcp pool 

# Ver MACs falsas
Router# show ip dhcp binding
```

## Parámetros

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| MAC src | RandMAC() | MAC aleatoria única |
| MAC dst | ff:ff:ff:ff:ff:ff | Broadcast |
| IP src/dst | 0.0.0.0 / 255.255.255.255 | DHCP estándar |
| Puertos | 68 → 67 | Cliente → Servidor |
| Message Type | DISCOVER | Solicitud de IP |
| Transaction ID | RandInt() | ID único por paquete |

## Resultados esperados

### Antes del Ataque

<img width="975" height="127" alt="image" src="https://github.com/user-attachments/assets/bfd40c30-2128-4c0c-9f9e-94129efda131" />
<img width="807" height="496" alt="image" src="https://github.com/user-attachments/assets/8b2f0a75-a82d-4ea4-8366-68b5867ae2fc" />


### Durante el Ataque

<img width="720" height="263" alt="image" src="https://github.com/user-attachments/assets/a91bc9c2-e5af-4fad-897e-16f73c3fd505" />
<img width="975" height="307" alt="image" src="https://github.com/user-attachments/assets/bd75ac64-5efa-4c6e-b0cf-67c41b770eb1" />


Se aprecian los bindings falsos con MACs aleatorias.

<img width="889" height="530" alt="image" src="https://github.com/user-attachments/assets/3205af45-2d16-4eed-b7c1-ee2dc2424a94" />

El Pool de la VLAN 20 se ha agotado, ya que se han entregado todas las direcciones IP.

<img width="338" height="113" alt="image" src="https://github.com/user-attachments/assets/9c46eb14-be92-4177-aabf-b8c35d48fbcd" />

Se aprecia que la PC víctima se ha quedado sin IP, porque no encuentra el servidor DHCP, y esto pasa porque el servidor está saturado por todos los bindings continuos que el ataque envía.

## Limpieza Post-Ataque

```bash
Router# clear ip dhcp binding *
Router# clear ip dhcp conflict *
```

## Medidas de Mitigación

### 1. DHCP Snooping

Examina los mensajes DHCP y solo permite aquellos mensajes que provienen de fuentes confiables. Ejemplo de aplicación:

```cisco
Switch(config)# ip dhcp snooping
Switch(config)# ip dhcp snooping vlan 20
Switch(config)# interface Gi0/1
Switch(config-if)# ip dhcp snooping trust
Switch(config)# interface range Gi0/2 - 24
Switch(config-if-range)# ip dhcp snooping limit rate 5
```

### 2. Port Security

Limita el número de direcciones MAC permitidas por puerto del switch.

```cisco
Switch(config)# interface Gi0/2
Switch(config-if)# switchport port-security
Switch(config-if)# switchport port-security maximum 2
Switch(config-if)# switchport port-security violation restrict
```

### 3. Rate Limiting (ACL)

Limita la cantidad de tráfico DHCP permitido por segundo.

```cisco
Router(config)# access-list 100 permit udp any any eq bootps
Router(config)# class-map DHCP-TRAFFIC
Router(config-cmap)# match access-group 100
Router(config)# policy-map LIMIT-DHCP
Router(config-pmap-c)# police 8000 conform-action transmit exceed-action drop
```

### 4. Lease Time Reducido

Reduce el tiempo que las IPs permanecen asignadas.

```cisco
Router(config-dhcp)# lease 0 0 30 #30 minutos
```

## Disclaimer

Uso exclusivo para:

- Laboratorios GNS3/PNETLab
- Educación en ciberseguridad

**Responsabilidad:** El autor NO se responsabiliza por uso indebido.
