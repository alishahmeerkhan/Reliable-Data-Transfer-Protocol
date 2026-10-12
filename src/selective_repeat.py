import threading
from rich import print
from packets import Packet

class SRSender:
    def __init__(self, window_size, seq_bits, timeout_duration, channel, receiver):
        self.window_size = window_size
        self.seq_bits = seq_bits
        self.max_seq = 2 ** seq_bits
        self.timeout_duration = timeout_duration
        self.channel = channel
        self.receiver = receiver
        self.base = 0
        self.next_seqnum = 0
        self.buffer = {}
        self.timers = {}
        self.acked_status = {}

    def send_data(self, payload):
        if len(self.buffer) >= self.window_size:
            print(f'[bold yellow]LOG: Window full, refusing new data.[/bold yellow]')
            return

        packet = Packet(seq_num=self.next_seqnum, is_ack=False, payload=payload)
        self.buffer[self.next_seqnum] = packet
        self.acked_status[self.next_seqnum] = False

        print(f'[bold yellow]LOG: Sender sending packet {packet.seq_num}.[/bold yellow]')
        self.channel.transmit(packet, self.receiver)

        self.start_timer(self.next_seqnum)
        self.next_seqnum = (self.next_seqnum + 1) % self.max_seq

    def receive_packet(self, ack_packet):
        if ack_packet.isCorrupted():
            print(f'[bold yellow]LOG: Sender received corrupted ACK, ignoring.[/bold yellow]')
            return

        ack_num = ack_packet.seq_num
        print(f'[bold yellow]LOG: Sender received individual ACK {ack_num}.[/bold yellow]')

        self.acked_status[ack_num] = True
        self.end_timer(ack_num)
        self.start_timer(self.next_seqnum)

        
        while self.acked_status.get(self.base, False) == True:
            self.buffer.pop(ack_num)
            self.timers.pop(self.base)
            self.acked_status.pop(self.base)

            self.base = (self.base + 1) % self.max_seq

    def on_timeout(self, seq_num):
        print(f'[bold yellow]LOG: Sender Timeout for {seq_num}. Retransmitting single packet.[/bold yellow]')
        self.start_timer(seq_num)
        self.channel.transmit(self.buffer[seq_num], self.receiver)

    def start_timer(self, seq_num):
        self.stop_timer()
        self.timers[seq_num] = threading.Timer(self.timeout_duration, self.on_timeout, args=(seq_num,))
        self.timer[seq_num].start()

    def end_timer(self, seq_num):
        if self.timers[seq_num] not in self.timers or self.timers[seq_num] is not None:
            self.timer.cancel()

class SRReceiver:
    def __init__(self, window_size, seq_bits, channel, sender):
        self.window_size = window_size
        self.seq_bits = seq_bits
        self.max_seq = 2 ** seq_bits
        self.channel = channel
        self.sender = sender
        self.base = 0
        self.buffer = {}

    def receive_packet(self, packet):
        if packet.isCorrupted():
            print(f'[bold yellow]LOG: Receiver dropped corrupted packet {packet.seq_num}.[/bold yellow]')
            return

        seq_num = packet.seq_num
        print(f'[bold yellow]LOG: Receiver received packet {seq_num}.[/bold yellow]')

        ack_packet = Packet(seq_num=seq_num, is_ack=True)
        self.channel.transmit(ack_packet, self.sender)

        if self.is_in_window(seq_num):
            self.buffer[seq_num] = packet.payload

            
            while self.base in self.buffer:
                self.deliver_data(packet.payload)
                self.buffer.pop(self.base)
                self.base = (self.base + 1) % self.max_seq

    def is_in_window(self, seq_num):
        diff = (seq_num - self.base) % self.max_seq
        return diff < self.window_size

    def deliver_data(self, payload):
        with open('received_data_sr.txt', 'a') as file:
            file.write(payload)