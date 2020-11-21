from m5.params import *
from m5.SimObject import SimObject

class Injector(SimObject):
    type = 'Injector'
    cxx_class = 'FaultInjector::Injector'
    cxx_header = 'injector/injector.hh'

    ISA = Param.String("", "target ISA to perform injection")
    injPC = Param.String("", "target injection PC")
    injReg = Param.String("", "Register to inject into")
    injBit = Param.Int(0,"Bit position to flip")
    injTick = Param.Tick(0, "tick to inject fault")
    regType = Param.Int(0, "type of register (0 = int, 1 = float, 2 = double)")
    srcDest = Param.Int(0, "source or destinate register (0 = src, 1 = dest")
    timeout = Param.Tick(500000000000, "timeout ticks")
    goldenFile = Param.String("", "Filename of golden trace")
