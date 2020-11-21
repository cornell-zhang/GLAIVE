#include "debug/Inj.hh"
#include "sim/sim_exit.hh"
#include "injector/injector.hh"

#include <fstream>
#include <iostream>

using namespace X86ISA;

namespace FaultInjector
{

void FI::FlipBit(Tick _injTick, int injR, int injBit, int regType)
{
    uint64_t currVal; // = thread->readIntReg(injR);
    uint64_t bitMask= 1 << injBit;

    if (regType == 0)
    {
        currVal = thread->readIntReg(injR); 
        thread->setIntReg(injR, currVal ^ bitMask); // flip bit using mask
    }
    else if (regType == 1)  // floating point register
    {
        currVal = thread->readFloatRegBits(injR);
        thread->setFloatRegBits(injR, currVal ^ bitMask);
    }
    else if (regType == 2)  // double precision register (SPARC)
    {
        bool upper = false;
        if (injBit >= 32) // flipping higher order bits
        {
            upper = true;
            bitMask = 1 << (injBit - 32);
        }
        if (upper)
        {
            currVal = thread->readFloatRegBits(injR);
            thread->setFloatRegBits(injR, currVal ^ bitMask);
        }
        else
        {
            currVal = thread->readFloatRegBits(injR+1);
            thread->setFloatRegBits(injR+1, currVal ^ bitMask);
        }
    }
}

Injector::Injector(InjectorParams *params) : 
    SimObject(params),
    ISA(params->ISA),
    injPC(params->injPC),
    injBit(params->injBit),
    injTick(params->injTick),
    injReg(params->injReg),
    regType(params->regType),
    srcDest(params->srcDest),
    timeoutVal(params->timeout),
    goldenFile(params->goldenFile)
{
    

    if (goldenFile != "")
    {
        

        std::ifstream goldFile(goldenFile);
        if (goldFile.is_open())
        {
            std::string line, strInjTick;
            bool started = false;

            strInjTick = std::to_string(injTick); // look for first tick before filling vector

            while (std::getline(goldFile, line))
            {
                if (!started)
                {
                    if (line.find(strInjTick) != std::string::npos)
                    {
                        started = true;
                    }
                }
                if (started)
                    goldenTrace.push_back(line);
            }
            goldFile.close();
        }
    }
    

    //DPRINTF("Testing object!\n");
}

void Injector::PerformFI(ThreadContext* _thread, Tick _when, 
                      Tick _injTick, std::string ISA, std::string desiredR, int injBit, int regType)
{
    FI fi(_thread, _when, ISA);
    int injR = archMap[ISA][regType][desiredR];
    fi.FlipBit(_when, injR, injBit, regType);
}

void Injector::trackState(std::string faultyTrace, std::string goldenTrace)
{
    if (goldenTrace != faultyTrace)
    {
        exitSimLoop("Diff trace\n");
    }
}

}   // end namespace


FaultInjector::Injector* InjectorParams::create()
{
    return new FaultInjector::Injector(this);
}

