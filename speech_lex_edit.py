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
# Speech lexicon editor in tkinker
#
# Tested with Ubuntu Linux and Mac Os X
#
# The tts, marrytts, phonetics and sequiturclient submodules are adapted from https://github.com/gooofy/py-nltools are
# https://github.com/gooofy/py-marytts
# The submodules are also licensed under the Apache 2.0 license, see headers

from tkinter import *
from functools import partial
from datetime import datetime
from tkinter import simpledialog
from tkinter import messagebox as mbox

import tts
import sequiturclient
import sys
import os
import platform

sequitur_model = "dicts/de_g2p_model-6"
todo_wordlist = "todo_wordlist.txt"
output_lexicon = "output_lexicon.txt"
auto_save = True

tts_client = tts.TTS()

# you can configure key bindings here. Note that we need different ones for Mac,
# as Cmd is standard for commands (instead of CTRL) and the F1-12 keys are buggy in tkinker on a Mac :/

key_bindings_mac = {"backup_btn": ("<Command-b>", "⌘+B"),
                      "change_g2p_textbox": ("<Command-g>", "⌘+G"),
                      "add_and_next": ("<Command-Return>", "⌘+↵"),
                      "number_key": ("<Command-Key-%d>", "⌘+%d"),
                      "play_btn_hotkey": ("<Command-p>", "⌘+P"),
                      "find_btn_hotkey": ("<Command-f>", "⌘+F")
}

key_bindings_pc = {"backup_btn": ("<Control-b>", "Ctrl+B"),
                      "change_g2p_textbox": ("<Control-g>", "Ctrl+G"),
                      "add_and_next": ("<Control-Return>", "Ctrl+↵"),
                      "number_key": ("<F%d>", "F%d"),
                      "play_btn_hotkey": ("<F12>", "F12"),
                      "find_btn_hotkey": ("<Control-f>", "Ctrl+F")
}

# determine if we running on a Mac (and need different key bindings)
if platform.system() == 'Darwin':
    key_bindings = key_bindings_mac
else:
    key_bindings = key_bindings_pc

def load_wordlist(wordlist):
    wordlist_ret = []
    with open(wordlist, 'r') as wordlist_reader:
        for line in wordlist_reader:
            if line[-1] == '\n':
                line = line[:-1]
            wordlist_ret.append(line)
    return wordlist_ret

def play(phn, async_play=True):
    tts_client.say_phn(phn, async_play=async_play)

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

def onselect_dictbox(evt, input_phn_text, input_word_text):
    w = evt.widget

    cursel = w.curselection()
    if cursel is not None and len(cursel) > 0:
        index = int(cursel[0])
        value = w.get(index)

        print('You selected item %d: "%s"' % (index, value))

        word, phn = value.split(' | ')

        if input_phn_text:
            input_phn_text.delete(0, END)
            input_phn_text.insert(0, phn)

        if input_word_text:
            input_word_text.delete(0, END)
            input_word_text.insert(0, word)

        try:
            play(phn, async_play=True)
        except:
            mbox.showinfo("Error", "Error in playback. Is MARY running?")


def onselect_wordbox(evt, window, proba_lbls, phn_lbls, phn_play_btns, copy_btns,
                     input_phn_text, input_word_text, num_variants=5):
    w = evt.widget
    cursel = w.curselection()

    if cursel is not None and len(cursel) > 0:
        index = int(cursel[0])
        value = w.get(index)
        print('You selected item %d: "%s"' % (index, value))

        change_g2p(value, window, proba_lbls, phn_lbls, phn_play_btns, copy_btns, input_phn_text, input_word_text)

# same as change_g2p_textbox, but allows an event agrument (for key binding)
def change_g2p_textbox_evt(evt, window, proba_lbls, phn_lbls, phn_play_btns, copy_btns, input_phn_text,
                           input_word_text, num_variants=5):
    change_g2p_textbox(window, proba_lbls, phn_lbls, phn_play_btns, copy_btns, input_phn_text,
                       input_word_text, num_variants)

# same as change_g2p, but with a textbox
def change_g2p_textbox(window, proba_lbls, phn_lbls, phn_play_btns, copy_btns, input_phn_text,
                       input_word_text, num_variants=5):
    word = input_word_text.get()
    change_g2p(word, window, proba_lbls, phn_lbls, phn_play_btns, copy_btns, input_phn_text,
                   input_word_text, num_variants)

# reload automatically generated phoneme entry suggestions
def change_g2p(word, window, proba_lbls, phn_lbls, phn_play_btns, copy_btns, input_phn_text,
               input_word_text, num_variants=5):

    # setting g2p proba and text labels to loading
    for row_num in range(num_variants):
        if row_num == 0:
            phn_lbls[row_num].config(text='loading...')
            proba_lbls[row_num].config(text='loading...')
        else:
            phn_lbls[row_num].config(text='')
            proba_lbls[row_num].config(text='')

    if input_phn_text:
        input_phn_text.delete(0, END)
        input_phn_text.insert(0, '')

    if input_word_text:
        input_word_text.delete(0, END)
        input_word_text.insert(0, word)

    # basically flush changes
    window.update_idletasks()

    phn_input_list = sequiturclient.sequitur_gen_phn_variants(sequitur_model, word, variants=num_variants)

    for row_num in range(num_variants):
        phn_lbls[row_num].config(text=phn_input_list[row_num]['phn'])
        proba_lbls[row_num].config(text=phn_input_list[row_num]['proba'])
        phn_play_btns[row_num+1].config(command=partial(play, phn_input_list[row_num]['phn']))
        copy_btns[row_num].config(command=partial(copy, phn_input_list[row_num]['phn'], input_phn_text))

        window.bind(key_bindings["number_key"][0] % (row_num+1), partial(play_evt, phn=phn_input_list[row_num]['phn']))

        bind_num = 10 - num_variants + row_num+1
        if platform.system() == 'Darwin' and bind_num == 10:
            bind_num = 0

        window.bind(key_bindings["number_key"][0] % bind_num, partial(copy_evt,
                                                                             phn=phn_input_list[row_num]['phn'],
                                                                             input_text=input_phn_text))

    if input_phn_text:
        input_phn_text.delete(0, END)
        input_phn_text.insert(0, phn_input_list[0]['phn'])

# delete one entry form the dictionary list box
def delete_entry(listDict):
    listDict.delete(ACTIVE)
    if auto_save:
        print("Active entry deleted.")
        save(listDict, output_lexicon)

def next_selection(listNodes):
    selection_indices = listNodes.curselection()

    # default next selection is the beginning
    next_selection = 0

    # make sure at least one item is selected
    if len(selection_indices) > 0:
        # Get the last selection, remember they are strings for some reason
        # so convert to int
        last_selection = int(selection_indices[-1])

        # clear current selections
        listNodes.selection_clear(selection_indices)

        # Make sure we're not at the last item
        if last_selection < listNodes.size() - 1:
            next_selection = last_selection + 1

    listNodes.activate(next_selection)
    listNodes.selection_set(next_selection)

    listNodes.event_generate("<<ListboxSelect>>", when="tail")

    return next_selection

# add an element and automatically select the next one
def add_and_next(listDict, listNodes, input_word_text, input_phn_text):
    entry = input_word_text.get() + ' | ' + input_phn_text.get()
    listDict.insert(END, entry)
    if auto_save:
        print("Added entry:" + entry)
        save(listDict, output_lexicon)

    sel_id = next_selection(listNodes)
    print('Add and next: selecting new element with id', sel_id)

def add_and_next_evt(evt, listDict, listNodes, input_word_text, input_phn_text):
    add_and_next(listDict, listNodes, input_word_text, input_phn_text)

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

def load(listDict, filename):

    if os.path.isfile(filename):
        print("Loading dictionary from:", filename)
        with open(filename, 'r') as in_file:
            for line in in_file:

                if line[-1] == '\n':
                    line = line[:-1]
                split = line.split(" ")
                word = split[0]
                phn = " ".join(split[1:])

                listDict.insert(END, word + " | " + phn)
    else:
        print("Warning, not loading dictionary since there was none:", filename)

def search_listdict(search_string, listDict_items, exact_match=False, split=''):
    search_index = -1

    # case insensitive search
    search_string = search_string.lower()

    for i, elem in enumerate(listDict_items):
        if exact_match:
            if elem.lower() == search_string:
                search_index = i
                return search_index
        else:
            if search_string in elem.lower():
                search_index = i
                return search_index

    return search_index

def setSelection(listDict, i):
    selection_indices = listDict.curselection()
    if selection_indices is not None and len(selection_indices) > 0:
        # clear current selections
        listDict.selection_clear(selection_indices)
    listDict.activate(i)
    listDict.selection_set(i)
    #listDict.event_generate("<<ListboxSelect>>", when="tail")

def search_listboxes(window, listDict, listNodes):
    search_string = simpledialog.askstring("Search", "Input search string:",
                                    parent=window)

    if search_string is None or len(search_string) == 0:
        return

    exact_match = False
    if search_string[0] == '^':
        exact_match = True

    listDict_items = [elem.split(' | ')[0] for elem in listDict.get(0, END)]
    print("listDict_items", listDict_items)
    listDict_index = search_listdict(search_string, listDict_items, exact_match)

    listNodes_items = listNodes.get(0, END)
    print("listNodes_items:",listNodes_items)
    listNodes_index = search_listdict(search_string, listNodes_items, exact_match)

    # found matching element, first select on nodes
    if listNodes_index != -1:
        setSelection(listNodes, listNodes_index)
    else:
        print(search_string, "not found")

    # found matching element, then on dict (might clear the selection in nodes though)
    if listDict_index != -1:
        setSelection(listDict, listDict_index)
    else:
        print(search_string, "not found")

def search_listboxes_evt(evt, window, listDict, listNodes):
    return search_listboxes(window, listDict, listNodes)

def save_and_exit(listDict):
    save(listDict, output_lexicon)
    if mbox.askyesno('Verify', 'Do you really want to quit?'):
        sys.exit()
    else:
        mbox.showinfo('No', 'Quit has been cancelled')

def backup(listDict):
    now = datetime.now()
    dt_string = now.strftime("%Y_%m_%d____%H_%M_%S")
    filename = "backup_" + dt_string + ".dict"
    save(listDict, "dicts/" + filename)

def backup_evt(evt,listDict):
    backup(listDict)

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

    play_btn_hotkey = key_bindings["play_btn_hotkey"][0]
    play_btn_hotkey_text = key_bindings["play_btn_hotkey"][1]

    play_btn = Button(window, text="Play (" + play_btn_hotkey_text + ")", command=partial(play_text,
                                                                                     input_text=input_phn_text))
    play_btn.grid(column=2, row=8)
    phn_play_btns.append(play_btn)

    window.bind(play_btn_hotkey, partial(play_text_evt, input_text=input_phn_text))

    row_num_offet = 2

    # Labels (probability, auto phoneme sequence) + play + copy buttons for all phoneme variants (usually 5)
    for row_num in range(num_variants):
        proba_lbl = Label(window, text=phn_input_list[row_num]['proba'])
        proba_lbl.grid(column=0, row=row_num+row_num_offet)
        proba_lbls.append(proba_lbl)

        lbl = Label(window, text=phn_input_list[row_num]['phn'])

        lbl.grid(column=1, row=row_num+row_num_offet)

        phn_lbls.append(lbl)

        # also bind to F1-F5 hot keys, or cmd+1 - cmd+5 on Mac
        play_btn = Button(window, text="Play ("+key_bindings["number_key"][1] % (row_num+1)+")")
        play_btn.grid(column=2, row=row_num+row_num_offet)
        phn_play_btns.append(play_btn)

        # also bind to F6-F10 hot keys, or cmd+6 - cmd+0 on Mac
        bind_num = 10 - num_variants + row_num+1
        if platform.system() == 'Darwin' and bind_num == 10:
            bind_num = 0

        copy_btn = Button(window, text="Copy ("+key_bindings["number_key"][1] % bind_num+")")
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
    listNodes.bind('<<ListboxSelect>>', partial(onselect_wordbox, window=window, proba_lbls=proba_lbls,
                                                phn_lbls=phn_lbls, phn_play_btns=phn_play_btns, copy_btns=copy_btns,
                                                input_phn_text=input_phn_text, input_word_text=input_word_text,
                                                num_variants=num_variants))
    scrollbar.config(command=listNodes.yview)

    frm2 = Frame(window)
    frm2.grid(row=1, column=1, sticky=N + S)

    scrollbar2 = Scrollbar(frm2, orient="vertical")
    scrollbar2.pack(side=RIGHT, fill=Y)

    listDict = Listbox(frm2, height=20,  width=40, yscrollcommand=scrollbar2.set, font=("Helvetica", 12))
    listDict.pack(expand=True, fill=Y)
    listDict.bind('<<ListboxSelect>>', partial(onselect_dictbox, input_phn_text=input_phn_text,
                                               input_word_text=input_word_text))
#    listSelection.grid(row=1, column=1, sticky=E + W + N)

    scrollbar2.config(command=listDict.yview)

    for x in load_wordlist(todo_wordlist):
        listNodes.insert(END, x)

    # Load the current dictionary in output_lexicon into th GUI
    load(listDict, output_lexicon)

    add_and_next_btn = Button(window, text="Add&Next ("+key_bindings["add_and_next"][1]+")", command=partial(add_and_next, listDict=listDict,
                                                                                listNodes=listNodes,
                                                                                input_word_text=input_word_text,
                                                                                input_phn_text=input_phn_text))
    add_and_next_btn.grid(column=3, row=8)

    window.bind(key_bindings["add_and_next"][0], partial(add_and_next_evt, listDict=listDict, listNodes=listNodes,
                                            input_word_text=input_word_text, input_phn_text=input_phn_text))

    delete_btn = Button(window, text="Delete Entry", command=partial(delete_entry, listDict))
    delete_btn.grid(column=2, row=1)

    save_and_exit_btn = Button(window, text="Save&Exit", command=partial(save_and_exit, listDict))
    save_and_exit_btn.grid(column=3, row=1)

    backup_btn = Button(window, text="Backup ("+key_bindings["backup_btn"][1]+")", command=partial(backup, listDict))
    backup_btn.grid(column=4, row=1)

    window.bind(key_bindings["backup_btn"][0], partial(backup_evt, listDict=listDict))

    reload_g2p_btn = Button(window, text="↻G2P ("+key_bindings["change_g2p_textbox"][1]+")", command=partial(change_g2p_textbox,  window=window,
                                                                 proba_lbls=proba_lbls, phn_lbls=phn_lbls,
                                                                 phn_play_btns=phn_play_btns,  copy_btns=copy_btns,
                                                                 input_phn_text=input_phn_text,
                                                                 input_word_text=input_word_text))

    window.bind(key_bindings["change_g2p_textbox"][0], partial(change_g2p_textbox_evt,  window=window,
                                                                 proba_lbls=proba_lbls, phn_lbls=phn_lbls,
                                                                 phn_play_btns=phn_play_btns,  copy_btns=copy_btns,
                                                                 input_phn_text=input_phn_text,
                                                                 input_word_text=input_word_text))

    reload_g2p_btn.grid(column=4, row=8)

    change_g2p("test", window, proba_lbls, phn_lbls, phn_play_btns, copy_btns, input_phn_text, input_word_text)

    window.bind(key_bindings["find_btn_hotkey"][0], partial(search_listboxes_evt, window=window, listDict=listDict, listNodes=listNodes))

    window.mainloop()

start_window()