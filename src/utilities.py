from time import time
from rich import print

class SimulationConfig:
    def __init__(self, protocol, num_packets, window_size, seq_bits, timeout_duration, loss_prob, 
                 corrupt_prob, delay_prob, delay_time):
        self.protocol = protocol
        self.num_packets = num_packets
        self.window_size = window_size
        self.seq_bits = seq_bits
        self.timeout_duration = timeout_duration
        self.loss_prob = loss_prob
        self.corrupt_prob = corrupt_prob
        self.delay_prob = delay_prob
        self.delay_time = delay_time

class SimulationStats:
    def __init__(self):
        self.total_transmitted = 0
        self.retransmission = 0
        self.successful_deliveries = 0
        self.start_time = 0.0
        self.end_time = 0.0

    def start_timer(self):
        self.start_time = time()

    def stop_timer(self):
        self.end_time = time()

    def get_execution_time(self):
        return self.end_time - self.start_time

    def increament_transmitted(self):
        self.total_transmitted += 1

    def increament_retransmitted(self):
        self.retransmission += 1
        self.total_transmitted += 1

    def increament_delivery(self):
        self.successful_deliveries += 1

    def get_report(self):
        print('[bold white]--- Simulation Results ---[/bold white]')
        print(f'[white]Total Packets Transmitted:   [/white][bright_cyan]{self.total_transmitted}[/bright_cyan]')
        print(f'[white]Total Packets Retransmitted: [/white][bright_cyan]{self.retransmission}[/bright_cyan]')
        print(f'[white]Total Successful Deliveries: [/white][bright_cyan]{self.successful_deliveries}[/bright_cyan]')
        print(f'[white]Total Execution Time:        [/white][bright_cyan]{self.get_execution_time():.6f} seconds[/bright_cyan]')