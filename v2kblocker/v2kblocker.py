from os import path
from glob import glob

import librosa
import numpy as np
import soundfile

from playsound import playsound


BASE = path.realpath(path.join(path.dirname(__file__), '..', 'data'))


class V2KBlocker:
    def __init__(self, sounds: list, avg_sample_len: int):
        super().__init__()

        self.sounds = sounds
        self.avg_sample_len = avg_sample_len

        self.dirs = {
            'noise': path.join(BASE, 'noise'),
            'voice': path.join(BASE, 'voice'),
            'woodpecker': path.join(BASE, 'woodpecker'),
        }

        self.audio = {}
        self.output = None

    def play(self):
        sr = 22050

        print(f'Creating randomized audio..')
        for sound in self.sounds:
            print(f'Processing "{sound}" channel..')
            if not self.audio.get(sound):
                self.audio[sound] = {}

            for fp in glob(path.join(self.dirs[sound], '*.wav')):
                sound_data = [

                    [], []]

                print(f'Processing file "{fp}"..')
                data, sr = librosa.load(fp, mono=False, sr=sr)
                samples_ms = data[0].size / (sr * self.avg_sample_len)
                variations = np.random.normal(samples_ms, 1.5, 1024)

                for i in [0, 1]:
                    channel = 'left' if i == 0 else 'right'

                    print(f'Processing {channel} channel..')
                    print('Calculating variable segment times..')
                    cuts = []
                    last = 0
                    while last < data.size:
                        cuts.append(int(np.random.choice(variations, size=1, replace=True)))
                        last += cuts[-1]

                    print(f'Calculated {len(cuts)} cuts of variable duration')
                    print('Segmenting audio..')

                    segments = []
                    idx = 0
                    for cut in cuts:
                        segments.append(data[i][idx:idx + cut])
                        idx += cut

                    print('Shuffling segments..')
                    np.random.shuffle(segments)

                    sound_data[i].extend(segments)

                self.audio[sound][fp] = sound_data

        print('Cropping to shortest channel length found in sounds..')

        lengths = []
        sounds = []
        for _, t in self.audio.items():
            for _, s in t:
                for _, c in s:
                    lengths.append(len(c))

        min_length = min(lengths)

        for kt, t in self.audio.items():
            for ks, s in t:
                s[0] = s[0:min_length]
                s[1] = s[1:min_length]

                sounds.append(np.array(s))

                self.audio[kt][ks] = None

        sound = sounds.pop()
        for s in sounds:
            sound[0, :] *= s[0, :]
            sound[1, :] *= s[1, :]

        self.output = librosa.util.normalize(sound)

        filename = path.join(BASE, 'render.wav')
        print(f'Saving to "{filename}"..')
        soundfile.write(filename, self.output, samplerate=int(sr), closefd=True)

        while True:
            print('(Re)starting playback..')
            playsound(filename)
