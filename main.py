#! /usr/bin/env python
import sys
import signal

from argparse import ArgumentParser

from v2kblocker import V2KBlocker

parser = ArgumentParser(prog='v2kblocker', description='Randomized micro-sampling V2K audio renderer')

parser.add_argument('-a', '--all', action='store_true', default=True, help='Use all sounds (default)')
parser.add_argument('-n', '--noise', action='store_true', default=False, help='Use noise sound')
parser.add_argument('-v', '--voice', action='store_true', default=False, help='Use voice sound')
parser.add_argument('-w', '--woodpecker', action='store_true', default=False, help='Use woodpecker sound')
parser.add_argument('-l', '--avg-smp-len', type=int, nargs=1, default=1000, help='Avg. sample length (ms)',
                    required=False)


def sig_handler(sig, frame):
    print('Bye.')
    sys.exit(0)


signal.signal(signal.SIGINT, sig_handler)

if __name__ == '__main__':
    args = parser.parse_args(sys.argv[1:])
    sounds = []
    for sound in ['noise', 'voice', 'woodpecker']:
        if args.__contains__(sound) or args.all:
            sounds.append(sound)

    V2KBlocker(sounds, args.avg_smp_len).play()
