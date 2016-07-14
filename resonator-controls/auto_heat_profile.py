"""Specifies how the current through the heating resistor should depend on the temperature.
No proportional control yet, just discrete steps.
Regardless of the function mechanism, needs to take temp as input and return a current (float) in amps"""


#maps temperature intervals to currents
STEP_DICT = {   (0, 4): 0.0,  (4, 100): 0.4,     (100, 200): 0.4,   (200, 250): 0.2, (250,300): 0}



STEP_DICT_FAST = { (0, 4): 0.0, (4, 200):0.4, (200, 250):0.3, (250, 280):0.2, (280, 290):0.1, (290, 300):0}

STEP_DICT_FASTER = { (0, 4):0.0, (4, 285):0.4, (285, 289):0.3, (289,290):0.2, (290,300): 0}

STEP_DICT_FASTEST = { (0, 4): 0, (4, 290): 0.4, (290, 300): 0}

def ininterval(x, tup):
    return ( x >= tup[0]) and (x < tup[1])



def step(temp, dy):
    for interval in dy.keys():
        if ininterval(temp, interval):
            return dy[interval]
    return 0

def step_std(temp):
    return step(temp, STEP_DICT)

def step_fast(temp):
    return step(temp, STEP_DICT_FAST)

def step_faster(temp):
    return step(temp, STEP_DICT_FASTER)

def step_fastest(temp):
    return step(temp, STEP_DICT_FASTEST)

FUNCS = {'step_std': step_std,   'step_fast': step_fast, 'step_faster': step_faster, 'step_fastest':step_fastest}



def get_func(s):
    return FUNCS[s]


def new_current(temp, func_string):
    func = get_func(func_string)
    return func(temp)
