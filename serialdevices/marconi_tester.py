import labrad


def wait(fn=None):
    if fn is None:
        raw_input("<Enter> to continue test")
    elif hasattr(fn, '__call__'):
        def waitAfterFn(*args):
            fn(*args)
            wait()
        return waitAfterFn

@wait
def init_marconi(ms):
    ms.frequency(1)
    ms.amplitude(1)
    ms.carrierstate(False)

@wait
def sweep_test(ms):
    print "Starting sweep test"

    ms.carriermode('SWEPT')
    ms.sweepmode('SNGL')
    ms.sweepshape('LIN')
    ms.sweeprange(0, 1)
    ms.sweepstep(0.1)
    ms.sweeptime(5)
    
    wait()

    ms.sweepbegin()
    wait()

    ms.sweepreset()
    wait()

    ms.sweepbegin()
    wait()
    ms.sweeppause()
    wait()
    ms.sweepcontinue()
    wait()

    "Sweep test completed"


def marconi_test():
    cxn = labrad.connect()
    ms = cxn.marconi_server()

    init_marconi(ms)
    sweep_test(ms)



if __name__ == "__main__":
    marconi_test()
