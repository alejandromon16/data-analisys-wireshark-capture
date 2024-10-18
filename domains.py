import csv
import socket
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd

def reverse_dns_lookup(ip):
    """Try to resolve the IP to a domain name."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return None

def parse_csv(filename, limit=20):
    """Parse the CSV file and collect destination IPs, limited to a certain number of rows."""
    requests_per_domain = defaultdict(int)

    with open(filename, mode='r') as file:
        csv_reader = csv.DictReader(file)
        count = 0
        for row in csv_reader:
            if count >= limit:
                break
            destination_ip = row['Destination IP']
            if destination_ip:  # Only process rows with a valid destination IP
                domain = reverse_dns_lookup(destination_ip)
                if domain:
                    requests_per_domain[domain] += 1
                else:
                    requests_per_domain[destination_ip] += 1
            count += 1

    return requests_per_domain

def plot_and_save_graph(domain_requests):
    """Plot the domain requests and save as PNG."""
    domains = list(domain_requests.keys())
    requests = list(domain_requests.values())

    # Create the bar chart
    plt.figure(figsize=(10, 6))
    plt.barh(domains, requests, color='skyblue')
    plt.xlabel('Number of Requests')
    plt.ylabel('Domains/IPs')
    plt.title('Domain Requests (First 20 Entries)')
    plt.tight_layout()

    # Save the plot as a PNG file
    plt.savefig('domain_requests.png')
    plt.show()

def save_to_csv(domain_requests):
    """Save the domain requests to a CSV file."""
    df = pd.DataFrame(list(domain_requests.items()), columns=['Domain/IP', 'Requests'])
    df.to_csv('domain_requests.csv', index=False)

def main():
    filename = 'capture_full_data.csv'
    domain_requests = parse_csv(filename, limit=1000)

    # Plot and save the graph
    plot_and_save_graph(domain_requests)

    # Save the domain requests to a CSV file
    save_to_csv(domain_requests)

    print("Graph saved as 'domain_requests.png' and data saved as 'domain_requests.csv'")

if __name__ == "__main__":
    main()
