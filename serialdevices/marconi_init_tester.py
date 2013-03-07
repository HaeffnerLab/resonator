import labrad
ms = labrad.connect().marconi_server()

ms.carrieronoff()
ms.amplitude()
ms.frequency()

ms.carriermode()
ms.sweeprangestart()
ms.sweeprangestop()
ms.sweepstep()
ms.sweeptime()
ms.sweepmode()
ms.sweepshape()
ms.sweeptrigmode()
