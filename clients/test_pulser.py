import labrad
import time

cxn = labrad.connect()
pulser = cxn.pulser()

count = 0
while (count <= 10):
    time.sleep(5)
    pulser.switch_manual("422", False)
    time.sleep(3)
    pulser.switch_manual("375", False)
    time.sleep(3)
    pulser.switch_manual("OvenLaser", False)
    time.sleep(3)
    pulser.switch_manual("Thermometer", False)
    time.sleep(3)
    pulser.switch_manual("422", True)
    pulser.switch_manual("375", True)
    pulser.switch_manual("OvenLaser", True)
    pulser.switch_manual("Thermometer", True)
    count += 1