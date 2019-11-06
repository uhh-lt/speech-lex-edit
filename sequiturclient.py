#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2019 Benjamin Milde (Universitaet Hamburg)
# Copyright 2016, 2017 Guenter Bartsch
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
# crude sequitur g2p interface
#

import logging
import tempfile
import traceback
import subprocess
# import misc

from phonetics import xsampa2ipa


def run_command(command, capture_stderr=True):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT if capture_stderr else subprocess.PIPE)
    return iter(p.stdout.readline, b'')


def sequitur_gen_phn_variants(modelfn, word, variants=5, quiet=False, replaceDash=True):
    xs = []

    with tempfile.NamedTemporaryFile() as f:

        if replaceDash:
            word = word.replace("-","")

        f.write((u'%s\n' % word).encode('utf8'))
        f.flush()

        cmd = ['g2p.py', '--encoding=UTF8', "--variants-number=" + str(variants), '--model', modelfn, '--apply', f.name]

        res = run_command(cmd)

        logging.debug('%s' % ' '.join(cmd))

        for l in res:

            line = l.strip()

            line = line.decode('utf8', errors='ignore')

            if not quiet:
                print(line)

            logging.debug('%s' % line)

            if 'stack usage:' in line:
                continue

            if word in line:
                parts = line.split('\t')

                if len(parts) < 4:
                    continue

                phn = {'proba': parts[2], 'phn': parts[3]}
                # print 'XS', xs
                xs.append(phn)
                # ipa = xsampa2ipa(word, xs)

    return xs


def sequitur_gen_phn(modelfn, word):
    xs = ''

    with tempfile.NamedTemporaryFile() as f:

        f.write((u'%s\n' % word).encode('utf8'))
        f.flush()

        cmd = ['g2p.py', '--encoding=UTF8', '--model', modelfn, '--apply', f.name]

        res = run_command(cmd)

        logging.debug('%s' % ' '.join(cmd))

        for l in res:

            line = l.strip()

            line = line.decode('utf8', errors='ignore')

            logging.debug('%s' % line)

            if 'stack usage:' in line:
                continue

            if word in line:
                parts = line.split('\t')

                if len(parts) < 2:
                    continue

                xs = parts[1]
                # print 'XS', xs

                # ipa = xsampa2ipa(word, xs)

    return xs


def sequitur_gen_phn_multi(modelfn, words):
    phn_map = {}

    with tempfile.NamedTemporaryFile() as f:

        for word in words:
            f.write((u'%s\n' % word).encode('utf8'))
        f.flush()

        cmd = ['g2p.py', '--encoding=UTF8', '--model', modelfn, '--apply', f.name]

        res = run_command(cmd, capture_stderr=False)

        logging.debug('%s' % ' '.join(cmd))

        for l in res:

            line = l.strip()

            line = line.decode('utf8', errors='ignore')

            logging.debug('%s' % line)

            if 'stack usage:' in line:
                continue

            parts = line.split('\t')

            if len(parts) < 2:
                continue

            try:
                word = parts[0]
                if word in words:
                    xs = parts[1]
                    # print 'XS', xs

                    # ipa = xsampa2ipa(word, xs)
                    phn_map[word] = xs
            except:
                logging.error("Error processing line %s:" % line)
                logging.error(traceback.format_exc())

    return phn_map
