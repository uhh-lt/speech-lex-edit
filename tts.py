#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2016, 2017, 2018 Guenter Bartsch
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#
# Abstraction layer for multiple TTS engines (Mary TTS, SVOX Pico TTS and eSpeak NG at the moment)
# can run those locally or act as a client for our HTTP TTS server
#

import logging
import requests
import urllib

from phonetics import ipa2mary, mary2ipa, ipa2xsampa, xsampa2ipa
from marytts import MaryTTS
import sequiturclient
import io

import simpleaudio as sa

MARY_VOICES = {

    'en_US': { 'male':   ["cmu-rms-hsmm", "dfki-spike", "dfki-obadiah", "dfki-obadiah-hsmm", "cmu-bdl-hsmm"],
               'female': ["cmu-slt-hsmm", "dfki-poppy", "dfki-poppy-hsmm", "dfki-prudence", "dfki-prudence-hsmm"]
             },

    'de_DE': { 'male':   ["bits3", "bits3-hsmm", "dfki-pavoque-neutral", "dfki-pavoque-neutral-hsmm", "dfki-pavoque-styles"],
               'female': ["bits1-hsmm"]
             }
    }

DEFAULT_MARY_VOICE   = 'dfki-pavoque-neutral'
DEFAULT_MARY_LOCALE  = 'de_DE'


class TTS(object):

    def __init__(self, 
                 host_tts    =        'local', 
                 port_tts    =           8300, 
                 locale      =        DEFAULT_MARY_LOCALE,
                 engine      =         'mary', 
                 voice       = DEFAULT_MARY_VOICE,
                 pitch       =             50,  # 0-99
                 speed       =            175): # approx. words per minute

        self._host_tts = host_tts
        self._port_tts = port_tts
        self._locale   = locale
        self._engine   = engine
        self._voice    = voice
        self._pitch    = pitch
        self._speed    = speed

        if host_tts == 'local':
            self.marytts = MaryTTS()
            self.picotts = None # lazy-loading to reduce package dependencies

    @property
    def locale(self):
        return self._locale
    @locale.setter
    def locale(self, v):
        self._locale = v

    @property
    def engine(self):
        return self._engine
    @engine.setter
    def engine(self, v):
        self._engine = v

    @property
    def voice(self):
        return self._voice
    @voice.setter
    def voice(self, v):
        self._voice = v

    @property
    def pitch(self):
        return self._pitch
    @pitch.setter
    def pitch(self, v):
        self._pitch = v

    @property
    def speed(self):
        return self._speed
    @speed.setter
    def speed(self, v):
        self._speed = v

    def synthesize(self, txt, mode='txt'):

        if self._host_tts == 'local':

            # import pdb; pdb.set_trace()

            wav = None

            if self.engine == 'mary':

                self.marytts.voice = self._voice
                self.marytts.locale = self._locale

                if mode == 'txt':
                    wav = self.marytts.synth_wav(txt)
                elif mode == 'ipa':
                    xs = ipa2mary('ipa', txt)
                    wav = self.marytts.synth_wav(xs, fmt='xs')
                elif mode == 'mary':
                    wav = self.marytts.synth_wav(txt, fmt='xs')
                else:
                    raise Exception("unknown mary mode '%s'" % mode)

            elif self.engine == 'pico':

                if mode == 'txt':

                    if not self.picotts:
                        from picotts import PicoTTS
                        self.picotts = PicoTTS()

                    self.picotts.voice = self._voice
                    wav = self.picotts.synth_wav (txt)
                    # logging.debug ('synthesize: %s %s -> %s' % (txt, mode, repr(wav)))

                else:
                    raise Exception("unknown pico mode '%s'" % mode)
            else:

                raise Exception("unknown engine '%s'" % self.engine)

        else:

            args = {'l': self._locale,
                    'v': self._voice,
                    'e': self._engine,
                    'm': mode,
                    't': txt.encode('utf8')}
            url = 'http://%s:%s/tts/synth?%s' % (self._host_tts, self._port_tts, urllib.urlencode(args))

            response = requests.get(url)

            if response.status_code != 200:
                return None

            wav = response.content

        if wav:
            logging.debug ('synthesize: %s %s -> WAV' % (txt, mode))
        else:
            logging.error ('synthesize: %s %s -> NO WAV' % (txt, mode))

        return wav

    def play_wav(self, wav, async_play=False):

        if self._host_tts == 'local':

            if wav:
                with io.BytesIO(wav) as tmp_buffer:
                    wave_read = sa.wave.open(tmp_buffer, 'rb')
                    wave_obj = sa.WaveObject.from_wave_read(wave_read)
                    play_obj = wave_obj.play()
                    if async_play == False:
                        play_obj.wait_done()
            else:
                raise Exception('no wav data given')

        else:

            url = 'http://%s:%s/tts/play' % (self._host_tts, self._port_tts)
                          
            if async_play:
                url += '?async=t'

            response = requests.post(url, data=wav)

    def say(self, utterance, async_play=False):

        wav = self.synthesize(utterance)
        self.play_wav(wav, async_play=async_play)

    def say_phn(self, phn, phn_format='mary', async_play=False):

        wav = self.synthesize(phn, mode=phn_format)
        self.play_wav(wav, async_play=async_play)

    def gen_phn(self, word, model='dicts/de_g2p_model-6', phn_format='mary'):

        if self._host_tts == 'local':

            if self.engine == 'mary':

                self.marytts.voice  = self._voice
                self.marytts.locale = self._locale

                mp = self.marytts.g2p(word)
                if phn_format == 'mary':
                    return mp
                elif phn_format == 'ipa':
                    return mary2ipa(word, mp)
                else:
                    raise Exception("Format not supported: '%s'" % phn_format)

            elif self.engine == 'sequitur':

                return sequiturclient.sequitur_gen_ipa(model, word)

            else:
                raise Exception ("unknown engine '%s'" % self.engine)

        else:
            args = {'l': self._locale,
                    'v': self._voice,
                    'e': self._engine,
                    't': word.encode('utf8')}
            url = 'http://%s:%s/tts/g2p?%s' % (self._host_tts, self._port_tts, urllib.urlencode(args))

            response = requests.get(url)

            if response.status_code != 200:
                return None

            return response.json()['ipa']

