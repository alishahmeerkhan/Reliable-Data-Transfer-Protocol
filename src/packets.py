import hashlib

class Packet:
    def __init__(self, seq_num, is_ack, payload=''):
        self.seq_num = seq_num
        self.is_ack = is_ack
        self.payload = payload
        self.check_sum = self.calculateCheckSum()

    def calculateCheckSum(self):
        check_sum_str = f'{self.seq_num} | {self.is_ack} | {self.payload}'.encode('utf-8')

        return hashlib.md5(check_sum_str).hexdigest()

    def isCorrupted(self):
        return self.calculateCheckSum() != self.check_sum