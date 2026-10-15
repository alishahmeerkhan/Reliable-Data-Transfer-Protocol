import argparse
from rich import print
from time import time, sleep
from unreliable_channel import UnreliableChannel
from go_back_n import GBNSender, GBNReceiver
from selective_repeat import SRSender, SRReceiver
from utilities import SimulationStats

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--protocol', required=True, choices=['gbn', 'sr'])

    parser.add_argument('--num_packets', type=int, default=200)
    parser.add_argument('--window_size', type=int, default=4)
    parser.add_argument('--seq_bits', type=int, default=3)
    parser.add_argument('--timeout', type=float, default=0.5)

    parser.add_argument('--loss_prob', type=float, default=0.0)
    parser.add_argument('--corrupt_prob', type=float, default=0.0)
    parser.add_argument('--delay_prob', type=float, default=0.0)
    parser.add_argument('--delay_time', type=float, default=0.005)

    parser.add_argument('--scenario', default=None, help='Name of the test scenario')

    return parser.parse_args()

def main():
    args = parse_arguments()
    stats = SimulationStats()

    channel = UnreliableChannel(args.loss_prob, args.corrupt_prob, args.delay_prob, args.delay_time, stats)

    if args.protocol == 'gbn':
        receiver = GBNReceiver(args.seq_bits, channel, sender=None)
        sender = GBNSender(args.window_size, args.seq_bits, args.timeout, channel, receiver)

        receiver.sender = sender

    elif args.protocol == 'sr':
        receiver = SRReceiver(args.window_size, args.seq_bits, channel, sender=None)
        sender = SRSender(args.window_size, args.seq_bits, args.timeout, channel, receiver)
        receiver.sender = sender

    print(f'[bold green]Starting Simulation for Protocol: [/bold green]{args.protocol}')
    stats.start_timer()

    current_packet = 0
    while current_packet < args.num_packets:
        payload = f'DATA PAYLOAD DUMMY {current_packet}'

        if len(sender.buffer) < args.window_size:
            sender.send_data(payload=payload)
            current_packet += 1
        else:
            sleep(0.1)

    while stats.successful_deliveries < args.num_packets:
        sleep(0.1)

    stats.stop_timer()
    stats.get_report()

    if args.scenario:
        stats.save_to_csv(args.protocol, args.scenario)

if __name__ == '__main__':
    main() 