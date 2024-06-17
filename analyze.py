import os
import re
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

metrics_dir = './metrics'
output_file = 'analysis_results.json'
pdf_output_file = 'workload_analysis.pdf'


def calculate_cost(read_units, write_units, hours=1):
    PRICE_PER_RCU_HOUR = 0.00013
    PRICE_PER_WCU_HOUR = 0.00065
    return (read_units * PRICE_PER_RCU_HOUR + write_units * PRICE_PER_WCU_HOUR) * hours


def parse_metrics(filename):
    with open(filename, 'r') as file:
        content = file.read()

    try:
        throughput = float(re.search(r'\[OVERALL\], Throughput\(ops/sec\), ([\d\.]+)', content).group(1))
    except AttributeError:
        throughput = 0.0

    def get_latency_percentile(content, percentile):
        try:
            return float(re.search(rf'\[READ\], {percentile}thPercentileLatency\(us\), ([\d\.]+)', content).group(1))
        except AttributeError:
            return None

    latencies = {
        'p50': get_latency_percentile(content, 50),
        'p75': get_latency_percentile(content, 75),
        'p90': get_latency_percentile(content, 90),
    }

    return throughput, latencies


def collect_metrics():
    results = {}
    for filename in os.listdir(metrics_dir):
        if filename.endswith('.txt') and not filename.endswith('_error.txt'):
            parts = filename.split('_')
            workload = parts[0]
            capacity = int(parts[1])

            throughput, latencies = parse_metrics(os.path.join(metrics_dir, filename))
            if workload not in results:
                results[workload] = []
            results[workload].append({
                'capacity': capacity,
                'throughput': throughput,
                'latencies': latencies
            })
    return results


def calculate_performance_per_dollar(metrics):
    for workload, data in metrics.items():
        for item in data:
            read_capacity = item['capacity']
            write_capacity = item['capacity']
            cost = calculate_cost(read_capacity, write_capacity)
            item['cost'] = cost
            item['performance_per_dollar'] = item['throughput'] / cost
    return metrics


def plot_workload(workload_name, workload_data, pdf):
    workload_data = sorted(workload_data, key=lambda x: x['capacity'])

    capacities = [entry['capacity'] for entry in workload_data]
    throughputs = [entry['throughput'] for entry in workload_data]
    p50s = [entry['latencies']['p50'] for entry in workload_data]
    p75s = [entry['latencies']['p75'] for entry in workload_data]
    p90s = [entry['latencies']['p90'] for entry in workload_data]
    performance_per_dollar = [entry['performance_per_dollar'] for entry in workload_data]
    costs = [entry['cost'] for entry in workload_data]


    plt.figure(figsize=(10, 15))

    plt.subplot(3, 1, 1)
    plt.plot(costs, throughputs, marker='o', linestyle='-')
    plt.xlabel('Cost ($)')
    plt.ylabel('Throughput (ops/sec)')
    plt.title(f'Workload: {workload_name} - Throughput vs. Cost')

    plt.subplot(3, 1, 2)
    plt.plot(costs, p50s, marker='o', linestyle='-', label='p50 Latency')
    plt.plot(costs, p75s, marker='o', linestyle='-', label='p75 Latency')
    plt.plot(costs, p90s, marker='o', linestyle='-', label='p90 Latency')
    plt.xlabel('Cost ($)')
    plt.ylabel('Latency (us)')
    plt.title(f'Workload: {workload_name} - Latency vs. Cost')
    plt.legend()

    plt.subplot(3, 1, 3)
    plt.plot(capacities, performance_per_dollar, marker='o', linestyle='-')
    plt.xlabel('Capacity (RCU/WCU)')
    plt.ylabel('Performance/$')
    plt.title(f'Workload: {workload_name} - Performance/$ vs. Capacity')

    plt.tight_layout()
    pdf.savefig()
    plt.close()

    optimal_point = max(workload_data, key=lambda x: x['performance_per_dollar'])
    print(f'Optimal point for {workload_name}:')
    print(f"  Capacity: {optimal_point['capacity']} RCU/WCU")
    print(f"  Throughput: {optimal_point['throughput']} ops/sec")
    print(f"  p50 Latency: {optimal_point['latencies']['p50']} us")
    print(f"  p75 Latency: {optimal_point['latencies']['p75']} us")
    print(f"  p90 Latency: {optimal_point['latencies']['p90']} us")
    print(f"  Performance/$: {optimal_point['performance_per_dollar']}")

def main():
    metrics = collect_metrics()
    metrics = calculate_performance_per_dollar(metrics)

    with open(output_file, 'w') as f:
        json.dump(metrics, f, indent=4)

    with PdfPages(pdf_output_file) as pdf:
        for workload_name, workload_data in metrics.items():
            print(f'Plotting results for {workload_name}')
            plot_workload(workload_name, workload_data, pdf)
    print(f'Results saved to {pdf_output_file}')

if __name__ == '__main__':
    main()

