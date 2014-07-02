## TODO: copy in relevant stuff from the MetatoneClassifier.
## Change timer so that every 1s it generates a new gesture for each player rather than classifies one.
## Otherwise -- everything else the same!

import random


def weighted_choice_sub(weights):
    rnd = random.random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i

 s = weighted_choice_sub(m[s])