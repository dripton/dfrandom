This program generates random GURPS Dungeon Fantasy characters.  It supports
all of the templates from GURPS Dungeon Fantasy 1: Adventurers.  It doesn't
support anything from the other books yet.

You need Python 2.7 or Python 3.x installed.  This program doesn't need
anything else, just libraries that come with Python.  (But if you want
to run the unit tests, you need py.test)

Usage:

python dfrandom.py

will give you a random character from a random template.

python dfrandom.py -t holy_warrior

will give you a random holy warrior.  (The underscore is there to avoid
issues with spaces on the command line.)

python dfrandom.py -h

will give you help.

Note that a random character is unlikely to be a very good character.  But
it might provide a decent starting point.

See LICENSE.txt for legal stuff.
