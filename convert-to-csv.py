import pyshark
import csv
import os
from tqdm import tqdm

# Paths
input_pcap = 'capture.pcapng'
output_csv = 'capture_full_data.csv'

# Verificar si el archivo PCAP existe
if not os.path.exists(input_pcap):
    raise FileNotFoundError(f"El archivo {input_pcap} no se encontró.")

# Definir los campos que deseas extraer
csv_fields = [
    'No.',
    'Time',
    'Source MAC',
    'Destination MAC',
    'Source IP',
    'Destination IP',
    'Source Port',
    'Destination Port',
    'Protocol',
    'Info',
    'Frame Length',
    'TTL',
    'TCP Flags',
    'Checksum Errors',
    'Layer 2 Protocol',
    'Dropped'
]

# Inicializar la captura de paquetes
cap = pyshark.FileCapture(
    input_pcap,
    use_json=True,
    include_raw=True,
    keep_packets=False  # Liberar memoria lo antes posible
)

# Abrir el archivo CSV para escritura
with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(csv_fields)  # Escribir la cabecera

    # Iterar sobre los paquetes con una barra de progreso
    for packet in tqdm(cap, desc="Procesando paquetes"):
        try:
            # Extraer información básica
            no = packet.number
            time = packet.sniff_time.strftime('%Y-%m-%d %H:%M:%S.%f') if hasattr(packet, 'sniff_time') else ''

            # Dirección MAC de origen y destino
            src_mac = packet.eth.src if 'eth' in packet else ''
            dst_mac = packet.eth.dst if 'eth' in packet else ''

            # Dirección IP de origen y destino
            src_ip = packet.ip.src if 'IP' in packet else ''
            dst_ip = packet.ip.dst if 'IP' in packet else ''

            # Puertos de origen y destino
            if 'TCP' in packet:
                src_port = packet.tcp.srcport
                dst_port = packet.tcp.dstport
                protocol = 'TCP'
                tcp_flags = packet.tcp.flags if hasattr(packet.tcp, 'flags') else ''
            elif 'UDP' in packet:
                src_port = packet.udp.srcport
                dst_port = packet.udp.dstport
                protocol = 'UDP'
                tcp_flags = ''
            elif 'ICMP' in packet:
                src_port = ''
                dst_port = ''
                protocol = 'ICMP'
                tcp_flags = ''
            else:
                src_port = ''
                dst_port = ''
                protocol = packet.highest_layer
                tcp_flags = ''

            # Información adicional
            info = packet.info if hasattr(packet, 'info') else ''

            # Longitud del frame
            frame_length = packet.length if hasattr(packet, 'length') else ''

            # TTL
            ttl = packet.ip.ttl if 'IP' in packet and hasattr(packet.ip, 'ttl') else ''

            # Errores de checksum
            checksum_errors = ''
            if 'TCP' in packet and hasattr(packet.tcp, 'checksum_status'):
                checksum_errors = packet.tcp.checksum_status
            elif 'UDP' in packet and hasattr(packet.udp, 'checksum_status'):
                checksum_errors = packet.udp.checksum_status
            elif 'IP' in packet and hasattr(packet.ip, 'checksum_status'):
                checksum_errors = packet.ip.checksum_status

            # Protocolo de la capa 2
            layer2_protocol = packet.eth.type if 'eth' in packet else ''

            # Paquetes descartados
            # Nota: PyShark no proporciona directamente esta información. Se requiere análisis adicional.

            # Preparar la fila
            row = [
                no,
                time,
                src_mac,
                dst_mac,
                src_ip,
                dst_ip,
                src_port,
                dst_port,
                protocol,
                info,
                frame_length,
                ttl,
                tcp_flags,
                checksum_errors,
                layer2_protocol,
                ''  # Campo 'Dropped' vacío, requiere métodos adicionales
            ]

            # Escribir la fila en el CSV
            csvwriter.writerow(row)

        except AttributeError as e:
            # Manejar paquetes que no tienen ciertos atributos
            pass
        except Exception as e:
            # Manejar cualquier otro error inesperado
            print(f"Error al procesar el paquete No.{packet.number}: {e}")
            pass

    # Cerrar la captura de paquetes
    cap.close()

print(f"Conversión a CSV completada: {output_csv}")
