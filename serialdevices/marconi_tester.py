import labrad


def wait(fn=None):
    if fn is None:
        raw_input("<Enter> to continue test")
    elif hasattr(fn, '__call__'):
        def waitAfterFn(*args):
            print "next test is: " + str(fn)
            wait()
            fn(*args)
            print "test at: " + str(fn) + " is completed"
        return waitAfterFn

@wait
def init_marconi(ms):
    ms.frequency(1)
    ms.amplitude(1)
    ms.carrierstate(False)

def init_sweep_test(ms):
    ms.carriermode('SWEPT')
    ms.sweepmode('SNGL')
    ms.sweepshape('LIN')

@wait
def sweep_test(ms, start, stop, step, time, triggered):
    print "Starting sweep test: initializing values"
    wait()
    init_sweep_test(ms)
    ms.sweeprange(start, stop)
    ms.sweepstep(step)
    ms.sweeptime(time)
    if triggered:
        ms.sweeptrigmode('STARTSTOP')

    print "starting first sweep: allow to finish"
    wait()
    ms.sweepbegin()

    print "reset sweep"
    wait()
    ms.sweepreset()

    print "start second sweep: pause in middle"
    wait()
    ms.sweepbegin()
    print "prepare to pause"
    wait()
    ms.sweeppause()
    print "ok. time to continue"
    wait()
    ms.sweepcontinue()

    print "<ENTER> to reset the sweep and end the test"
    wait()
    ms.sweepreset()
    print "Sweep test completed"


def marconi_test():
    cxn = labrad.connect()
    ms = cxn.marconi_server()

    init_marconi(ms)
    sweep_test(ms, 1, 3, .01, .1, True)


if __name__ == "__main__":
    marconi_test()
