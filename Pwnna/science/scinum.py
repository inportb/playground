# -*- coding: utf-8 -*-
from __future__ import division

class NumberWithUncertainty:
    def __init__(self, number, uncertainty, absolute=True):
        self.number = float(number)

        if absolute:
            self.absoluteUncertainty = float(uncertainty)
            try:
                self.percentageUncertainty = abs(self.absoluteUncertainty / self.number)
            except ZeroDivisionError:
                self.percentageUncertainty = 0.0
        else:
            self.percentageUncertainty = float(uncertainty)
            self.absoluteUncertainty = self.number * self.percentageUncertainty

        self.absolute = absolute

    def __add__(self, other):
        try:
            return NumberWithUncertainty(self.number + other, self.absoluteUncertainty)
        except TypeError:
            return NumberWithUncertainty(self.number + other.number, self.absoluteUncertainty + other.absoluteUncertainty)

    def __sub__(self, other):
        try:
            return NumberWithUncertainty(self.number - other, self.absoluteUncertainty)
        except TypeError:
            return NumberWithUncertainty(self.number - other.number, self.absoluteUncertainty + other.absoluteUncertainty)

    def __mul__(self, other):
        try:
            return NumberWithUncertainty(self.number * other, self.absoluteUncertainty)
        except TypeError:
            return NumberWithUncertainty(self.number * other.number, self.percentageUncertainty + other.percentageUncertainty, absolute=False)

    def __div__(self, other):
        try:
            return NumberWithUncertainty(self.number / other, self.absoluteUncertainty)
        except TypeError:
            return NumberWithUncertainty(self.number / other.number, self.percentageUncertainty + other.percentageUncertainty, absolute=False)

    def __truediv__(self, other):
        return self.__div__(other)

    def __eq__(self, other):
        return abs(self.number - other.number) < 0.1 # lolol hardcode. Change this. Someone help me.

    def showNumber(self, unit="", absolute=True):
        if unit:
            unit += " "
        print self.number, "%s/replace/" % unit, # Anyone know how to do the +/- sign? I can't get it working
        if absolute:
            print self.absoluteUncertainty, unit
        else:
            print self.percentageUncertainty*100, "%"

    def __str__(self):
        return "%.2f /replace/ %.2f" % (self.number, self.absoluteUncertainty) # lolol hardcode

def number(n, u):
    return NumberWithUncertainty(n, u)
