import threading
from rich import print
from pathlib import Path
from packets import Packet

class GBNSender:
    def __init__(self, window_size, seq_bits, timeout_duration, channel, receiver):
        self.window_size = window_size
        self.seq_bits = seq_bits
        self.max_seq = 2 ** seq_bits
        self.timeout_duration = timeout_duration
        self.channel = channel
        self.receiver = receiver
        self.base = 0
        self.next_seqnum = 0
        self.buffer = []
        self.timer = None

    def send_data(self, payload):
        if len(self.buffer) >= self.window_size:
            print(f'[bold yellow]LOG: Window full, refusing new data.[/bold yellow]')
            return

        packet = Packet(seq_num=self.next_seqnum, is_ack=False, payload=payload)
        self.buffer.append(packet)

        print(f'[bold yellow]LOG: Sender sending packet {packet.seq_num}[/bold yellow]')
        self.channel.stats.increament_transmitted()
        self.channel.transmit(packet, self.receiver)

        if self.base == self.next_seqnum:
            self.start_timer()

        self.next_seqnum = (self.next_seqnum + 1) % self.max_seq
        return

    def receive_packet(self, ack_packet):
        if ack_packet.isCorrupted():
            print(f'[bold yellow]LOG: Sender received corrupted ACK, ignoring.[/bold yellow]')
            return

        ack_num = ack_packet.seq_num
        print(f'[bold yellow]LOG: Sender received ACK {ack_num}.[/bold yellow]')
        unacked_seqs = [packet.seq_num for packet in list(self.buffer)]

        if ack_num in unacked_seqs:
            while len(self.buffer) > 0:
                popped_packet = self.buffer.pop(0)
                if popped_packet.seq_num == ack_num:
                    break

            self.base = (ack_num + 1) % self.max_seq

            self.stop_timer()
            if len(self.buffer) > 0:
                self.start_timer()

    def on_timeout(self):
        print(f'[bold yellow]LOG: Sender Timeout! Retransmitting all outstanding packets.[/bold yellow]')
        self.start_timer()

        for packet in list(self.buffer):
            print(f'[bold yellow]LOG: Sender retransmitting packet {packet.seq_num}.[/bold yellow]')
            self.channel.stats.increament_retransmitted()
            self.channel.transmit(packet, self.receiver)

    def start_timer(self):
        self.stop_timer()
        self.timer = threading.Timer(self.timeout_duration, self.on_timeout)
        self.timer.start()

    def stop_timer(self):
        if self.timer is not None:
            self.timer.cancel()

class GBNReceiver:
    def __init__(self, seq_bit, channel, sender):
        self.seq_bit = seq_bit
        self.max_seq = 2 ** seq_bit
        self.expected_seqnum = 0
        self.channel = channel
        self.sender = sender

    def receive_packet(self, packet):
        if packet.isCorrupted():
            print(f'[bold yellow]LOG: Receiver dropped corrupted packet {packet.seq_num}.[/bold yellow]')
            self.send_duplicate_ack()
            return

        if packet.seq_num != self.expected_seqnum:
            print(f'[bold yellow]LOG: Receiver discarded out-of-order packet {packet.seq_num}.[/bold yellow]')
            self.send_duplicate_ack()
            return

        print(f'[bold yellow]LOG: Receiver successfully received packet {packet.seq_num}.[/bold yellow]')

        self.deliver_data(packet.payload)

        ack_packet = Packet(seq_num=self.expected_seqnum, is_ack=True, payload='')
        print(f'[bold yellow]LOG: Receiver sending ACK {self.expected_seqnum}.[/bold yellow]')
        self.channel.stats.increament_transmitted()
        self.channel.transmit(ack_packet, self.sender)

        self.expected_seqnum = (self.expected_seqnum + 1) % self.max_seq

    def send_duplicate_ack(self):
        last_ack_num = (self.expected_seqnum - 1) % self.max_seq
        ack_packet = Packet(seq_num=last_ack_num, is_ack=True, payload='')
        print(f'[bold yellow]LOG: Receiver sending duplicate ACK {last_ack_num}.[/bold yellow]')
        self.channel.transmit(ack_packet, self.sender)

    def deliver_data(self, payload):
        path = Path(__file__).resolve().parent.parent / 'application_layer/received_data_gbn.txt'

        with open(path, 'a') as file:
            file.write(payload + '\n')
        self.channel.stats.increament_delivery()