Requirements:

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
