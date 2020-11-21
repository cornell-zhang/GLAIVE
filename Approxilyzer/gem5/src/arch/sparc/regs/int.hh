#ifndef __ARCH_SPARC_INTREGS_HH__
#define __ARCH_SPARC_INTREGS_HH__

namespace SparcISA
{
    enum IntRegIndex
    {
        G0,
        G1,
        G2,
        G3,
        G4,
        G5,
        G6,
        G7,

        O0,
        O1,
        O2,
        O3,
        O4,
        O5,
        O6,
        O7,

        L0,
        L1,
        L2,
        L3,
        L4,
        L5,
        L6,
        L7,

        I0,
        I1,
        I2,
        I3,
        I4,
        I5,
        I6,
        I7,
        
        NUM_INTREGS
    };
}

#endif // __ARCH_SPARC_INTREGS_HH__
