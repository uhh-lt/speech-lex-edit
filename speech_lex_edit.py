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
# speech lexicon editor in tkinker
#

from tkinter import *
from functools import partial
from datetime import datetime

import tts
import sequiturclient
import sys

sequitur_model = "dicts/de_g2p_model-6"
todo_wordlist = "todo_wordlist.txt"
output_lexicon = "output_lexicon.txt"
auto_save = True

tts_client = tts.TTS()


def load_wordlist(wordlist):
    wordlist_ret = []
    with open(wordlist, 'r') as wordlist_reader:
        for line in wordlist_reader:
            if line[-1] == '\n':
                line = line[:-1]
                wordlist_ret.append(line)
    return wordlist_ret

def play(phn):
    tts_client.say_phn(phn)

def play_evt(evt, phn):
    play(phn)

def play_text(input_text):
    tts_client.say_phn(input_text.get())

def play_text_evt(evt, input_text):
    play_text(input_text)

def copy(phn, input_text):
    if input_text:
        input_text.delete(0, END)
        input_text.insert(0, phn)

def copy_evt(evt, phn, input_text):
    copy(phn, input_text)

def onselect_wordbox(evt, window, proba_lbls, phn_lbls, phn_play_btns, copy_btns, input_phn_text, input_word_text, num_variants=5):
    w = evt.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    print('You selected item %d: "%s"' % (index, value))

    change_g2p(value, window, proba_lbls, phn_lbls, phn_play_btns, copy_btns, input_phn_text, input_word_text)

def change_g2p(word, window, proba_lbls, phn_lbls, phn_play_btns, copy_btns, input_phn_text, input_word_text, num_variants=5):
    phn_input_list = sequiturclient.sequitur_gen_phn_variants(sequitur_model, word, variants=num_variants)

    for row_num in range(num_variants):
        phn_lbls[row_num].config(text=phn_input_list[row_num]['phn'])
        proba_lbls[row_num].config(text=phn_input_list[row_num]['proba'])
        phn_play_btns[row_num+1].config(command=partial(play, phn_input_list[row_num]['phn']))
        copy_btns[row_num].config(command=partial(copy, phn_input_list[row_num]['phn'], input_phn_text))

        window.bind("<F"+str(row_num+1)+">", partial(play_evt, phn=phn_input_list[row_num]['phn']))

        window.bind("<F" + str(12 - num_variants + row_num+1) + ">", partial(copy_evt, phn=phn_input_list[row_num]['phn'], input_text=input_phn_text))

    if input_phn_text:
        input_phn_text.delete(0, END)
        input_phn_text.insert(0, phn_input_list[0]['phn'])

    if input_word_text:
        input_word_text.delete(0, END)
        input_word_text.insert(0, word)

def delete_entry(listDict):
    listDict.delete(ACTIVE)
    if auto_save:
        print("Active entry deleted.")
        save(listDict, output_lexicon)

def add_and_next(listDict, input_word_text, input_phn_text):
    entry = input_word_text.get() + ' | ' + input_phn_text.get()
    listDict.insert(END, entry)
    if auto_save:
        print("Added entry:" + entry)
        save(listDict, output_lexicon)

def add_and_next_evt(evt, listDict, input_word_text, input_phn_text):
    add_and_next(listDict, input_word_text, input_phn_text)

def save(listDict, filename):
    print("Saving dictionary to:", filename)
    all_items = listDict.get(0, END)
    print("Dictionary is:", all_items)
    with open(filename, 'w') as out_file:
        for elem in all_items:
            split = elem.split(' | ')
            word = split[0]
            phns = ' | '.join(split[1:])
            print(word, phns)
            out_file.write(word + ' ' + phns + '\n')

def save_and_exit(listDict):
    save(listDict, output_lexicon)
    sys.exit()

def backup(listDict):
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y__%H_%M_%S")
    filename = "backup_" + dt_string + ".dict"
    save(listDict, "dicts/" + filename)

def start_window(num_variants=5):
    window = Tk()

    window.title("Speech lex edit")
    window.geometry('1100x800')

    phn_input_list = sequiturclient.sequitur_gen_phn_variants(sequitur_model, "test", variants=num_variants)

    proba_lbls = []
    phn_lbls = []
    phn_play_btns = []
    copy_btns = []

    input_phn_text = Entry(window, width=20)
    input_phn_text.grid(column=1, row=8)

    input_word_text = Entry(window, width=20)
    input_word_text.grid(column=0, row=8)

    play_btn_hotkey = "F"+str(num_variants+1)

    play_btn = Button(window, text="Play (" + play_btn_hotkey + ")", command=partial(play_text, input_text=input_phn_text))
    play_btn.grid(column=2, row=8)
    phn_play_btns.append(play_btn)

    window.bind("<"+play_btn_hotkey+">", partial(play_text_evt, input_text=input_phn_text))

    row_num_offet = 2

    for row_num in range(num_variants):
        proba_lbl = Label(window, text=phn_input_list[row_num]['proba'])
        proba_lbl.grid(column=0, row=row_num+row_num_offet)
        proba_lbls.append(proba_lbl)

        lbl = Label(window, text=phn_input_list[row_num]['phn'])

        lbl.grid(column=1, row=row_num+row_num_offet)

        phn_lbls.append(lbl)

        play_btn = Button(window, text="Play (F"+str(row_num+1)+")") #, command=partial(play, phn_input_list[row_num]['phn']))
        play_btn.grid(column=2, row=row_num+row_num_offet)
        phn_play_btns.append(play_btn)

        copy_btn = Button(window, text="Copy (F"+str(12 - num_variants + row_num+1)+")") #, command=partial(copy, phn_input_list[row_num]['phn'], input_text))
        copy_btn.grid(column=3, row=row_num+row_num_offet)
        copy_btns.append(copy_btn)

    # frames and scrollbar

    frm = Frame(window)
    frm.grid(row=1, column=0, sticky=N + S)
    window.rowconfigure(1, weight=1)
    window.columnconfigure(1, weight=1)

    scrollbar = Scrollbar(frm, orient="vertical")
    scrollbar.pack(side=RIGHT, fill=Y)

    listNodes = Listbox(frm, width=20, yscrollcommand=scrollbar.set, font=("Helvetica", 12))
    listNodes.pack(expand=True, fill=Y)
    listNodes.bind('<<ListboxSelect>>', partial(onselect_wordbox, window=window, proba_lbls=proba_lbls, phn_lbls=phn_lbls,
                                                phn_play_btns=phn_play_btns, copy_btns=copy_btns, input_phn_text=input_phn_text,
                                                input_word_text=input_word_text, num_variants=num_variants))
    scrollbar.config(command=listNodes.yview)

    frm2 = Frame(window)
    frm2.grid(row=1, column=1, sticky=N + S)

    scrollbar2 = Scrollbar(frm2, orient="vertical")
    scrollbar2.pack(side=RIGHT, fill=Y)

    listDict = Listbox(frm2, height=20,  width=40, yscrollcommand=scrollbar2.set, font=("Helvetica", 12))
    listDict.pack(expand=True, fill=Y)
#    listSelection.grid(row=1, column=1, sticky=E + W + N)

    scrollbar2.config(command=listDict.yview)

    for x in load_wordlist(todo_wordlist):
        listNodes.insert(END, x)

    #for x in "ABCDEFGHIJKLLMNOP":
    #    listDict.insert(END, x + "|")

    add_and_next_btn = Button(window, text="Add&Next (Ctrl+↵)", command=partial(add_and_next, listDict, input_word_text, input_phn_text))
    add_and_next_btn.grid(column=3, row=8)

    window.bind("<Control-Return>", partial(add_and_next_evt, listDict=listDict, input_word_text=input_word_text, input_phn_text=input_phn_text))

    delete_btn = Button(window, text="Delete Entry", command=partial(delete_entry, listDict))
    delete_btn.grid(column=2, row=1)

    save_and_exit_btn = Button(window, text="Save&Exit", command=partial(save_and_exit, listDict))
    save_and_exit_btn.grid(column=3, row=1)

    save_and_exit_btn = Button(window, text="Backup", command=partial(backup, listDict))
    save_and_exit_btn.grid(column=4, row=1)

    change_g2p("test", window, proba_lbls, phn_lbls, phn_play_btns, copy_btns, input_phn_text, input_word_text)

    window.mainloop()

start_window()
