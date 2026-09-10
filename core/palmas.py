"""
Detector de duas palmas, rodando em paralelo à escuta por voz.

Serve como gatilho alternativo: bater duas palmas pausa/retoma o JARVIS,
útil para os momentos em que falar não é prático (ex: microfone ocupado
por outro programa) ou você só quer silenciá-lo rapidamente.
"""

import time
from collections import deque

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 44100
BLOCK_SIZE = 1024


class DetectorDePalmas:
    def __init__(self, on_duas_palmas, clap_window=1.2, cooldown=1.5,
                 threshold_multiplier=3.5, min_clap_gap=0.25):
        self.on_duas_palmas = on_duas_palmas
        self.clap_window = clap_window
        self.cooldown = cooldown
        self.threshold_mult = threshold_multiplier
        self.min_gap = min_clap_gap

        self.clap_times = deque()
        self.noise_floor = 0.01
        self.last_trigger_time = 0.0
        self.last_clap_time = 0.0
        self._stream = None

    def _process_block(self, indata):
        rms = float(np.sqrt(np.mean(indata**2)))
        now = time.time()

        if now - self.last_trigger_time < self.cooldown:
            self.noise_floor = 0.98 * self.noise_floor + 0.02 * rms
            return

        threshold = max(self.noise_floor * self.threshold_mult, 0.015)
        is_loud = rms > threshold

        if is_loud:
            if now - self.last_clap_time > self.min_gap:
                self.last_clap_time = now
                self.clap_times.append(now)
        else:
            self.noise_floor = 0.98 * self.noise_floor + 0.02 * rms

        while self.clap_times and (now - self.clap_times[0]) > self.clap_window:
            self.clap_times.popleft()

        if len(self.clap_times) >= 2 and (now - self.clap_times[-1]) > 0.35:
            self.clap_times.clear()
            self.last_trigger_time = now
            self.on_duas_palmas()

    def _callback(self, indata, frames, time_info, status):
        self._process_block(indata[:, 0])

    def iniciar(self):
        self._stream = sd.InputStream(
            channels=1, samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, callback=self._callback
        )
        self._stream.start()

    def parar(self):
        if self._stream:
            self._stream.stop()
            self._stream.close()
