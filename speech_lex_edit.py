from tkinter import *
from functools import partial

import tts
import sequiturclient

sequitur_model = "dicts/de_g2p_model-6"

tts_client = tts.TTS()

def play(phn):
    tts_client.say_phn(phn)

def play_text(input_text):
    tts_client.say_phn(input_text.get())

def copy(phn, input_text):
    if input_text:
        input_text.delete(0, END)
        input_text.insert(0, phn)

def start_window(num_variants=5):
    window = Tk()

    window.title("Speech lex edit")

    window.geometry('550x400')

    phn_input_list = sequiturclient.sequitur_gen_phn_variants(sequitur_model, "facebook", variants=num_variants)

    proba_lbls = []
    phn_lbls = []
    phn_play_btns = []
    copy_btns = []

    input_text = Entry(window, width=20)
    input_text.grid(column=0, row=6)

    play_btn = Button(window, text="Play", command=partial(play_text, input_text))
    play_btn.grid(column=2, row=6)
    phn_play_btns.append(play_btn)

    for row_num in range(num_variants):
        proba_lbl = Label(window, text=phn_input_list[row_num]['proba'])
        proba_lbl.grid(column=0, row=row_num)
        proba_lbls.append(proba_lbl)

        lbl = Label(window, text=phn_input_list[row_num]['phn'])

        lbl.grid(column=1, row=row_num)

        phn_lbls.append(lbl)

        play_btn = Button(window, text="Play", command=partial(play, phn_input_list[row_num]['phn']))
        play_btn.grid(column=2, row=row_num)
        phn_play_btns.append(play_btn)

        copy_btn = Button(window, text="Copy", command=partial(copy, phn_input_list[row_num]['phn'], input_text))
        copy_btn.grid(column=3, row=row_num)
        copy_btns.append(play_btn)

    window.mainloop()

start_window()