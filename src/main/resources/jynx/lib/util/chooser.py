# Original code by Mark Seaborn <http://lackingrhoticity.blogspot.com>
# Slight modifications by Kay Schluehr


class ModelCheckEscape(Exception):
    pass

class Chooser(object):
    def __init__(self, chosen, queue):
        self._chosen = iter(chosen)
        self._queue  = queue
        self._collected = []

    def choose(self, choices):
        try:
            choice = self._chosen.next()
            if choice not in choices:
                raise Exception("Program is not deterministic")
            self._collected.append(choice)
            return choice
        except StopIteration:
            self._queue+=[self._collected + [choice] for choice in choices]
            raise ModelCheckEscape()

def check(func, chooser = Chooser):
    queue = [[]]
    while len(queue) > 0:
        chosen = queue.pop(0)
        try:
            func(chooser(chosen, queue))
        except ModelCheckEscape:
            pass


