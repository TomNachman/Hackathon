"""
for this assignment this file is .py but it should by a config file ( .ini for example) and should be under .gitignore
"""
import random
from typing import Tuple, Union

# GLOBALS - CONSTANTS
UDP_PORT = 13117
TCP_PORT = 2016
UDP_IP = '172.1.255.255'  # convention ip for udp_ip broadcasting.
MAGIC_COOKIE = 0xabcddcba
MESSAGE_TYPE = 0x2
BUFFER_SIZE = 1024
# COLORS
HEADER = '\033[95m'
OK_BLUE = '\033[94m'
OK_CYAN = '\033[96m'
OK_GREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
END = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
RED = '\033[91m'
BG_GREEN = '\033[42m'

ops = {"+": (lambda x, y: x + y), "-": (lambda x, y: x - y), "*": (lambda x, y: x * y), "/": (lambda x, y: x / y)}
r = range(0, 9)


def generate_simple_math() -> Tuple[str, int]:
    while True:
        num1 = random.randint(1, 100)
        num2 = random.randint(1, 100)
        operation = random.choice(list(ops.keys()))
        msg = f"{OK_BLUE}How much is " + str(num1) + operation + str(num2) + "?\n"
        answer = ops[operation](num1, num2)
        if answer in r:
            return msg, answer

