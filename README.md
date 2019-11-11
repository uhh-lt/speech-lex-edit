# Speech lex edit

Speech lex edit is a phonetic lexicon editor for ASR and TTS systems. You can use it to create lexicon entries for OOV semi-automatically, i.e. pronounciation entries are suggested by a G2P model and can be manually edited. Feedback is provided by synthesizing the phonetic entry with a TTS engine. The intended target language is German, but it should be relatively straightforward to use it with another language, as long as it is compatible with [MARY](http://mary.dfki.de/).

# Screenshot

![Speech-lex-edit screenshot](https://raw.githubusercontent.com/uhh-lt/speech-lex-edit/master/screenshot.png "Speech-lex-edit screenshot")

# Installation

Speech lex edit is a Python3 program (cross-platform GUI with tkinter) and tested on Linux and Mac OS X. Playback of phonetic entries needs the simpleaudio package and the requests module to communicate with [MARY](http://mary.dfki.de/). Furthermore you need an installation of the G2P software [Sequitur G2P](https://github.com/sequitur-g2p/) (also Python software) and the TTS software [MARY](http://mary.dfki.de/) (Java). See below:

## Requirements:

pip3 install simpleaudio requests

simpleaudio is needed for audio output, the requests module is used to communicate with mary.

Install sequitur G2P:

You can install sequitur G2P on Linux and on Mac OS X, dependencies are swig and Python. It is now possible to install the latest version of sequitur-g2p with python3 by using the newest version in Git: 

sudo apt-get install swig #Ubuntu Linux
brew install swig # Mac OS X

pip3 install git+https://github.com/sequitur-g2p/sequitur-g2p@master

Note, when installing on MacOS, you might run into issues due to the default libc being from clang. The error might look like:

./Multigram.hh:34:10: fatal error: 'unordered_map' file not found 

If that is the case, try installing it with either:

CPPFLAGS="-stdlib=libstdc++" pip3 install git+https://github.com/sequitur-g2p/sequitur-g2p@master
 
Or tell pip to use a real gcc compiler, as installed with brew (gcc/g++ usually also point to clang):

brew install gcc@7

CXX=g++-7 CC=gcc-7 pip3 install git+https://github.com/sequitur-g2p/sequitur-g2p@master

You may need to install with sudo.

Then download mary, e.g. https://github.com/marytts/marytts/releases/download/v5.2/marytts-5.2.zip

Unzip and cd marytts-5.2/

Then run the component installer:
./bin/marytts-component-installer

And install DFKIs unit selection voice for German (one of the best available):
dfki-pavoque-neutral

# Running

After you've installed the requirements, you should be able to run the program with python3 speech-lex-edit.py

A g2p model is necessary and there is a precomputed one for German in this repository.
