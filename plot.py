import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def load_analysis_results(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


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
    analysis_results = load_analysis_results('analysis_results.json')
    pdf_output_file = 'workload_analysis.pdf'

    with PdfPages(pdf_output_file) as pdf:
        for workload_name, workload_data in analysis_results.items():
            print(f'Plotting results for {workload_name}')
            plot_workload(workload_name, workload_data, pdf)
    print(f'Results saved to {pdf_output_file}')

if __name__ == '__main__':
    main()

