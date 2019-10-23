#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright 2019 Benjamin Milde (Universitaet Hamburg)
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

import sequiturclient
import math

import multiprocessing
from joblib import Parallel, delayed

input_vocabulary = "voc.txt"
output_file = "voc_todo.txt"
sequitur_model = "dicts/de_g2p_model-6"
num_variants = 3
cutoff = 1000
num_read = 0
candidate_dict = []
num_cores = multiprocessing.cpu_count()

inputs = []

def process_word(elem):
    word, occs, num_read = elem

    try:
        phns = sequiturclient.sequitur_gen_phn_variants(sequitur_model, word, variants=num_variants, quiet=True)
        proba = phns[0]["proba"]
    except:
        print("Warning, automatic translation failed for: ", word)
        return (word, occs * -10.0, math.nan, occs)

    if num_read % 100 == 0:
        print("At word:", word, phns[0]["proba"], phns[0]["phn"])

    return (word, (1.0 - float(phns[0]["proba"])) * math.log10(float(occs)), float(phns[0]["proba"]), occs)

with open(input_vocabulary) as voc:
    for line in voc:
        if num_read > cutoff:
            break

        word, occs = line.split()
        occs = int(occs)

        inputs += [(word, occs, num_read)]

        num_read += 1

print("Loaded dictionary, now computing g2p candidate dictionary with confidences!")
candidate_dict = Parallel(n_jobs=num_cores)(delayed(process_word)(elem) for elem in inputs)

with open("voc_todo.txt", "w") as voc_todo:

    print("Sorting dict...")
    candidate_dict_sorted = sorted(candidate_dict, key=lambda kv: kv[1], reverse=True)

    for elem in candidate_dict_sorted:
        voc_todo.write(elem[0] + " " + str(elem[1]) + " " + str(elem[2]) + " " + str(elem[3]) + "\n")