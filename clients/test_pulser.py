import labrad
import time

cxn = labrad.connect()
pulser = cxn.pulser()
pulser.get_channels()
#Initially switch off the TTL pulse except the first one
pulser.switch_manual('Thermometer1', True)