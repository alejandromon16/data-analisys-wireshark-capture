import csv
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd

def parse_csv_for_volumes(filename):
    """Parse the CSV file and collect data volumes for each source and destination."""
    data_volumes = defaultdict(lambda: defaultdict(int))  # Nested dictionary: {Source: {Destination: Volume}}
    
    with open(filename, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            source_mac = row['Source MAC']
            destination_mac = row['Destination MAC']
            frame_length = row['Frame Length']

            if source_mac and destination_mac and frame_length:
                try:
                    frame_length = int(frame_length)
                    data_volumes[source_mac][destination_mac] += frame_length
                except ValueError:
                    continue  # In case 'Frame Length' is not a valid number

    return data_volumes

def create_graphs(data_volumes):
    """Create and save graphs showing data volumes for each source and destination."""
    source_total_volumes = defaultdict(int)
    destination_total_volumes = defaultdict(int)

    # Calculate total volumes sent by each source and received by each destination
    for source, destinations in data_volumes.items():
        for destination, volume in destinations.items():
            source_total_volumes[source] += volume
            destination_total_volumes[destination] += volume

    # Plot the data sent by each source
    plt.figure(figsize=(10, 6))
    sources = list(source_total_volumes.keys())
    volumes = list(source_total_volumes.values())
    plt.barh(sources, volumes, color='lightcoral')
    plt.xlabel('Total Data Volume (Bytes)')
    plt.ylabel('Source Devices')
    plt.title('Total Data Sent by Source Devices')
    plt.tight_layout()
    plt.savefig('data_sent_by_source.png')
    plt.show()

    # Plot the data received by each destination
    plt.figure(figsize=(10, 6))
    destinations = list(destination_total_volumes.keys())
    volumes = list(destination_total_volumes.values())
    plt.barh(destinations, volumes, color='lightblue')
    plt.xlabel('Total Data Volume (Bytes)')
    plt.ylabel('Destination Devices')
    plt.title('Total Data Received by Destination Devices')
    plt.tight_layout()
    plt.savefig('data_received_by_destination.png')
    plt.show()

def save_data_to_tables(data_volumes):
    """Save the data volumes into tables (CSV files)."""
    # Convert the data into a list of dictionaries for better handling in pandas
    data_list = []
    for source, destinations in data_volumes.items():
        for destination, volume in destinations.items():
            data_list.append({'Source MAC': source, 'Destination MAC': destination, 'Total Data Volume (Bytes)': volume})
    
    df = pd.DataFrame(data_list)
    df.to_csv('data_volumes.csv', index=False)

    # Show table output for the user
    print("Table of data volumes between source and destination:")
    print(df.head())

def main():
    filename = 'capture_full_data.csv'
    
    # Parse the CSV file and calculate the total volume of data sent by each source and destination
    data_volumes = parse_csv_for_volumes(filename)

    # Create graphs showing the total data sent by source devices and received by destinations
    create_graphs(data_volumes)

    # Save the data volumes into a CSV file and display the table
    save_data_to_tables(data_volumes)

if __name__ == "__main__":
    main()
