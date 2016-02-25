import random


def mega(size):
    return size * 1024 * 1024


def kilo(size):
    return size * 1024


def randstr(len):
    # http://stackoverflow.com/a/35161595/2050087
    return '%0x' % random.getrandbits(len * 4)
