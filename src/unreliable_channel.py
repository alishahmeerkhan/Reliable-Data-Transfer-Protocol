from rich import print
from time import sleep
import random, threading, copy

random.seed(2562)

class UnreliableChannel:
    def __init__(self, loss_prob, corrupt_prob, delay_prob, delay_time, stats):
        self.loss_prob = loss_prob
        self.corrupt_prob = corrupt_prob
        self.delay_prob = delay_prob
        self.delay_time = delay_time
        self.stats = stats

    def transmit(self, packet, destination):
        transmit_packet = copy.deepcopy(packet)

        if random.random() < self.loss_prob:
            print(f'[bold yellow]LOG: Packet/ACK {packet.seq_num} lost in channel.[/bold yellow]')
            return

        if random.random() < self.corrupt_prob:
            transmit_packet.payload = 'CORRUPTED_' + transmit_packet.payload
            print(f'[bold yellow]LOG: Packet/ACk {transmit_packet.seq_num} corrupted in channel.[/bold yellow]')

        if random.random() < self.delay_prob:
            print(f'[bold yellow]LOG: Packet/ACK {packet.seq_num} delayed in channel.[/bold yellow]')
            threading.Thread(target=self.wait_and_deliver, args=(transmit_packet, destination)).start()
            return

        destination.receive_packet(transmit_packet)

    def wait_and_deliver(self, packet, destination):
        sleep(self.delay_time)
        destination.receive_packet(packet)