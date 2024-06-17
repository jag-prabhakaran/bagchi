import subprocess
import os
import time

workloads = ['workloada', 'workloadb', 'workloadc', 'workloadd', 'workloade']
dynamodb_properties_path = '/Users/jag/Downloads/YCSB/YCSB/dynamodb/conf/dynamodb.properties'
output_dir = './metrics'
capacity_steps = [5, 10, 15, 20, 25]
table_name = 'usertable'  

def run_ycsb(workload, read_capacity, write_capacity):
    command = f'$YCSB_HOME/bin/ycsb run dynamodb -P workloads/{workload} -P {dynamodb_properties_path} -p dynamodb.readCapacityUnits={read_capacity} -p dynamodb.writeCapacityUnits={write_capacity}'
    print(f"Running command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(f"Command output: {result.stdout}")
    print(f"Command error: {result.stderr}")
    return result.stdout, result.stderr

def save_metrics(workload, read_capacity, write_capacity, metrics, errors):
    timestamp = int(time.time())
    filename = os.path.join(output_dir, f'{workload}_{read_capacity}_{write_capacity}_{timestamp}.txt')
    error_filename = os.path.join(output_dir, f'{workload}_{read_capacity}_{write_capacity}_{timestamp}_error.txt')
    with open(filename, 'w') as file:
        file.write(metrics)
    with open(error_filename, 'w') as file:
        file.write(errors)

def update_table_capacity(table_name, read_capacity, write_capacity):
    command = f'aws dynamodb update-table --table-name {table_name} --provisioned-throughput ReadCapacityUnits={read_capacity},WriteCapacityUnits={write_capacity}'
    print(f"Updating table capacity: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(f"Update command output: {result.stdout}")
    print(f"Update command error: {result.stderr}")

def main():
    os.makedirs(output_dir, exist_ok=True)
    for workload in workloads:
        for capacity in capacity_steps:
            print(f'Running YCSB workload: {workload} with capacity: {capacity} RCU/WCU')
            update_table_capacity(table_name, capacity, capacity)
            time.sleep(15)  
            metrics, errors = run_ycsb(workload, capacity, capacity)
            save_metrics(workload, capacity, capacity, metrics, errors)
            print(f'Finished workload: {workload} with capacity: {capacity} RCU/WCU')
            time.sleep(5)

if __name__ == '__main__':
    main()

