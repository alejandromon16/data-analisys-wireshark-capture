import pandas as pd
from mac_vendor_lookup import MacLookup
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de estilo para gráficos
sns.set(style="whitegrid")

# Inicializar MacLookup y actualizar la base de datos
mac_lookup = MacLookup()
try:
    mac_lookup.update_vendors()
except Exception as e:
    print(f"Error al actualizar la base de datos de MacLookup: {e}")

# Leer el archivo CSV generado previamente
input_csv = 'capture_full_data.csv'
df = pd.read_csv(input_csv)

# Verificar si las columnas 'Source MAC' y 'Destination MAC' existen
if 'Source MAC' in df.columns and 'Destination MAC' in df.columns:
    # Concatenar y obtener direcciones MAC únicas, eliminando NaNs
    mac_addresses = pd.concat([df['Source MAC'], df['Destination MAC']]).dropna().unique()
else:
    print("El archivo CSV no contiene columnas 'Source MAC' y 'Destination MAC'.")
    mac_addresses = []

if len(mac_addresses) > 0:
    # Crear un DataFrame para almacenar las MAC y sus fabricantes
    mac_df = pd.DataFrame(mac_addresses, columns=['MAC Address'])

    # Eliminar direcciones MAC ficticias o nulas
    mac_df = mac_df[mac_df['MAC Address'].str.strip().str.lower() != '00:00:00:00:00:00']

    # Función para obtener el fabricante
    def get_vendor(mac):
        try:
            return mac_lookup.lookup(mac)
        except:
            return 'Unknown'

    # Aplicar la función de fabricante con una barra de progreso
    tqdm.pandas(desc="Buscando fabricantes de MAC")
    mac_df['Vendor'] = mac_df['MAC Address'].progress_apply(get_vendor)

    # Función de clasificación de dispositivos
    def classify_device(vendor):
        vendor = vendor.lower()
        device_keywords = {
            'iPhone/iPad/Mac': ['apple'],
            'Smartphone/Tablets': ['samsung', 'huawei', 'honor', 'xiaomi', 'oneplus', 'oppo', 'vivo'],
            'Computadora': ['dell', 'hp', 'hewlett packard', 'lenovo', 'asus', 'acer', 'msi'],
            'Smart TV/Dispositivos Multimedia': ['sony', 'lg', 'panasonic', 'samsung', 'philips', 'vizio'],
            'Router/Dispositivos de Red': ['netgear', 'tp-link', 'd-link', 'asus', 'linksys', 'huawei'],
            'Dispositivos IoT': ['ikea', 'belkin', 'philips hue', 'tp-link', 'amazon', 'google'],
            'Otro': []
        }

        for device_type, keywords in device_keywords.items():
            for keyword in keywords:
                if keyword in vendor:
                    return device_type
        return 'Otro'

    # Aplicar la clasificación
    mac_df['Device Type'] = mac_df['Vendor'].apply(classify_device)

    # Análisis de dispositivos
    device_counts = mac_df['Device Type'].value_counts()
    print("Cantidad de dispositivos por tipo:")
    print(device_counts)

    # Guardar los resultados
    mac_df.to_csv('mac_classification.csv', index=False)
    device_counts.to_csv('device_counts.csv', header=['Count'])
    print("Clasificación de MAC guardada en 'mac_classification.csv'")
    print("Cantidad de dispositivos por tipo guardada en 'device_counts.csv'")

    # Visualización de dispositivos
    plt.figure(figsize=(12,8))
    sns.barplot(x=device_counts.values, y=device_counts.index, palette='viridis')
    plt.title('Cantidad de Dispositivos por Tipo')
    plt.xlabel('Cantidad')
    plt.ylabel('Tipo de Dispositivo')
    plt.tight_layout()
    plt.savefig('device_counts.png')
    plt.show()
else:
    print("No se encontraron direcciones MAC para clasificar.")
