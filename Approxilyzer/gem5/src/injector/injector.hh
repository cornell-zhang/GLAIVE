#ifndef __TEST_OBJ_TEST_OBJECT_HH__
#define __TEST_OBJ_TEST_OBJECT_HH__

#include "params/Injector.hh"
#include "sim/sim_object.hh"

#include "arch/sparc/regs/int.hh"
#include "arch/sparc/regs/float.hh"
#include "arch/x86/regs/int.hh"
#include "arch/x86/regs/float.hh"
#include "base/bigint.hh"
#include "base/types.hh"
#include "cpu/inst_seq.hh"
#include "cpu/static_inst.hh"

class ThreadContext;



namespace FaultInjector {

static std::map<std::string, int> SPARCIntRegConverter =
{
    {"g0", SparcISA::IntRegIndex::G0},
    {"g1", SparcISA::IntRegIndex::G1},
    {"g2", SparcISA::IntRegIndex::G2},
    {"g3", SparcISA::IntRegIndex::G3},
    {"g4", SparcISA::IntRegIndex::G4},
    {"g5", SparcISA::IntRegIndex::G5},
    {"g6", SparcISA::IntRegIndex::G6},
    {"g7", SparcISA::IntRegIndex::G7},

    {"o0", SparcISA::IntRegIndex::O0},
    {"o1", SparcISA::IntRegIndex::O1},
    {"o2", SparcISA::IntRegIndex::O2},
    {"o3", SparcISA::IntRegIndex::O3},
    {"o4", SparcISA::IntRegIndex::O4},
    {"o5", SparcISA::IntRegIndex::O5},
    {"o6", SparcISA::IntRegIndex::O6},
    {"o7", SparcISA::IntRegIndex::O7},

    {"l0", SparcISA::IntRegIndex::L0},
    {"l1", SparcISA::IntRegIndex::L1},
    {"l2", SparcISA::IntRegIndex::L2},
    {"l3", SparcISA::IntRegIndex::L3},
    {"l4", SparcISA::IntRegIndex::L4},
    {"l5", SparcISA::IntRegIndex::L5},
    {"l6", SparcISA::IntRegIndex::L6},
    {"l7", SparcISA::IntRegIndex::L7},

    {"i0", SparcISA::IntRegIndex::I0},
    {"i1", SparcISA::IntRegIndex::I1},
    {"i2", SparcISA::IntRegIndex::I2},
    {"i3", SparcISA::IntRegIndex::I3},
    {"i4", SparcISA::IntRegIndex::I4},
    {"i5", SparcISA::IntRegIndex::I5},
    {"i6", SparcISA::IntRegIndex::I6},
    {"i7", SparcISA::IntRegIndex::I7},

// an alternative to using exact index instead

    {"0", SparcISA::IntRegIndex::G0},
    {"1", SparcISA::IntRegIndex::G1},
    {"2", SparcISA::IntRegIndex::G2},
    {"3", SparcISA::IntRegIndex::G3},
    {"4", SparcISA::IntRegIndex::G4},
    {"5", SparcISA::IntRegIndex::G5},
    {"6", SparcISA::IntRegIndex::G6},
    {"7", SparcISA::IntRegIndex::G7},

    {"8", SparcISA::IntRegIndex::O0},
    {"9", SparcISA::IntRegIndex::O1},
    {"10", SparcISA::IntRegIndex::O2},
    {"11", SparcISA::IntRegIndex::O3},
    {"12", SparcISA::IntRegIndex::O4},
    {"13", SparcISA::IntRegIndex::O5},
    {"14", SparcISA::IntRegIndex::O6},
    {"15", SparcISA::IntRegIndex::O7},

    {"16", SparcISA::IntRegIndex::L0},
    {"17", SparcISA::IntRegIndex::L1},
    {"18", SparcISA::IntRegIndex::L2},
    {"19", SparcISA::IntRegIndex::L3},
    {"20", SparcISA::IntRegIndex::L4},
    {"21", SparcISA::IntRegIndex::L5},
    {"22", SparcISA::IntRegIndex::L6},
    {"23", SparcISA::IntRegIndex::L7},

    {"24", SparcISA::IntRegIndex::I0},
    {"25", SparcISA::IntRegIndex::I1},
    {"26", SparcISA::IntRegIndex::I2},
    {"27", SparcISA::IntRegIndex::I3},
    {"28", SparcISA::IntRegIndex::I4},
    {"29", SparcISA::IntRegIndex::I5},
    {"30", SparcISA::IntRegIndex::I6},
    {"31", SparcISA::IntRegIndex::I7}
};

static std::map<std::string, int> SPARCFloatRegConverter = 
{
    {"f0", SparcISA::FloatRegIndex::F0},
    {"f1", SparcISA::FloatRegIndex::F1},
    {"f2", SparcISA::FloatRegIndex::F2},
    {"f3", SparcISA::FloatRegIndex::F3},
    {"f4", SparcISA::FloatRegIndex::F4},
    {"f5", SparcISA::FloatRegIndex::F5},
    {"f6", SparcISA::FloatRegIndex::F6},
    {"f7", SparcISA::FloatRegIndex::F7},
    {"f8", SparcISA::FloatRegIndex::F8},
    {"f9", SparcISA::FloatRegIndex::F9},

    {"f10", SparcISA::FloatRegIndex::F10},
    {"f11", SparcISA::FloatRegIndex::F11},
    {"f12", SparcISA::FloatRegIndex::F12},
    {"f13", SparcISA::FloatRegIndex::F13},
    {"f14", SparcISA::FloatRegIndex::F14},
    {"f15", SparcISA::FloatRegIndex::F15},
    {"f16", SparcISA::FloatRegIndex::F16},
    {"f17", SparcISA::FloatRegIndex::F17},
    {"f18", SparcISA::FloatRegIndex::F18},
    {"f19", SparcISA::FloatRegIndex::F19},

    {"f20", SparcISA::FloatRegIndex::F20},
    {"f21", SparcISA::FloatRegIndex::F21},
    {"f22", SparcISA::FloatRegIndex::F22},
    {"f23", SparcISA::FloatRegIndex::F23},
    {"f24", SparcISA::FloatRegIndex::F24},
    {"f25", SparcISA::FloatRegIndex::F25},
    {"f26", SparcISA::FloatRegIndex::F26},
    {"f27", SparcISA::FloatRegIndex::F27},
    {"f28", SparcISA::FloatRegIndex::F28},
    {"f29", SparcISA::FloatRegIndex::F29},

    {"f30", SparcISA::FloatRegIndex::F30},
    {"f31", SparcISA::FloatRegIndex::F31},
    {"f32", SparcISA::FloatRegIndex::F32},
    {"f33", SparcISA::FloatRegIndex::F33},
    {"f34", SparcISA::FloatRegIndex::F34},
    {"f35", SparcISA::FloatRegIndex::F35},
    {"f36", SparcISA::FloatRegIndex::F36},
    {"f37", SparcISA::FloatRegIndex::F37},
    {"f38", SparcISA::FloatRegIndex::F38},
    {"f39", SparcISA::FloatRegIndex::F39},

    {"f40", SparcISA::FloatRegIndex::F40},
    {"f41", SparcISA::FloatRegIndex::F41},
    {"f42", SparcISA::FloatRegIndex::F42},
    {"f43", SparcISA::FloatRegIndex::F43},
    {"f44", SparcISA::FloatRegIndex::F44},
    {"f45", SparcISA::FloatRegIndex::F45},
    {"f46", SparcISA::FloatRegIndex::F46},
    {"f47", SparcISA::FloatRegIndex::F47},
    {"f48", SparcISA::FloatRegIndex::F48},
    {"f49", SparcISA::FloatRegIndex::F49},

    {"f50", SparcISA::FloatRegIndex::F50},
    {"f51", SparcISA::FloatRegIndex::F51},
    {"f52", SparcISA::FloatRegIndex::F52},
    {"f53", SparcISA::FloatRegIndex::F53},
    {"f54", SparcISA::FloatRegIndex::F54},
    {"f55", SparcISA::FloatRegIndex::F55},
    {"f56", SparcISA::FloatRegIndex::F56},
    {"f57", SparcISA::FloatRegIndex::F57},
    {"f58", SparcISA::FloatRegIndex::F58},
    {"f59", SparcISA::FloatRegIndex::F59},

    {"f60", SparcISA::FloatRegIndex::F60},
    {"f61", SparcISA::FloatRegIndex::F61},
    {"f62", SparcISA::FloatRegIndex::F62},
    {"f63", SparcISA::FloatRegIndex::F63},

// an alternative to using exact index instead

    {"0", SparcISA::FloatRegIndex::F0},
    {"1", SparcISA::FloatRegIndex::F1},
    {"2", SparcISA::FloatRegIndex::F2},
    {"3", SparcISA::FloatRegIndex::F3},
    {"4", SparcISA::FloatRegIndex::F4},
    {"5", SparcISA::FloatRegIndex::F5},
    {"6", SparcISA::FloatRegIndex::F6},
    {"7", SparcISA::FloatRegIndex::F7},
    {"8", SparcISA::FloatRegIndex::F8},
    {"9", SparcISA::FloatRegIndex::F9},

    {"10", SparcISA::FloatRegIndex::F10},
    {"11", SparcISA::FloatRegIndex::F11},
    {"12", SparcISA::FloatRegIndex::F12},
    {"13", SparcISA::FloatRegIndex::F13},
    {"14", SparcISA::FloatRegIndex::F14},
    {"15", SparcISA::FloatRegIndex::F15},
    {"16", SparcISA::FloatRegIndex::F16},
    {"17", SparcISA::FloatRegIndex::F17},
    {"18", SparcISA::FloatRegIndex::F18},
    {"19", SparcISA::FloatRegIndex::F19},

    {"20", SparcISA::FloatRegIndex::F20},
    {"21", SparcISA::FloatRegIndex::F21},
    {"22", SparcISA::FloatRegIndex::F22},
    {"23", SparcISA::FloatRegIndex::F23},
    {"24", SparcISA::FloatRegIndex::F24},
    {"25", SparcISA::FloatRegIndex::F25},
    {"26", SparcISA::FloatRegIndex::F26},
    {"27", SparcISA::FloatRegIndex::F27},
    {"28", SparcISA::FloatRegIndex::F28},
    {"29", SparcISA::FloatRegIndex::F29},

    {"30", SparcISA::FloatRegIndex::F30},
    {"31", SparcISA::FloatRegIndex::F31},
    {"32", SparcISA::FloatRegIndex::F32},
    {"33", SparcISA::FloatRegIndex::F33},
    {"34", SparcISA::FloatRegIndex::F34},
    {"35", SparcISA::FloatRegIndex::F35},
    {"36", SparcISA::FloatRegIndex::F36},
    {"37", SparcISA::FloatRegIndex::F37},
    {"38", SparcISA::FloatRegIndex::F38},
    {"39", SparcISA::FloatRegIndex::F39},

    {"40", SparcISA::FloatRegIndex::F40},
    {"41", SparcISA::FloatRegIndex::F41},
    {"42", SparcISA::FloatRegIndex::F42},
    {"43", SparcISA::FloatRegIndex::F43},
    {"44", SparcISA::FloatRegIndex::F44},
    {"45", SparcISA::FloatRegIndex::F45},
    {"46", SparcISA::FloatRegIndex::F46},
    {"47", SparcISA::FloatRegIndex::F47},
    {"48", SparcISA::FloatRegIndex::F48},
    {"49", SparcISA::FloatRegIndex::F49},

    {"50", SparcISA::FloatRegIndex::F50},
    {"51", SparcISA::FloatRegIndex::F51},
    {"52", SparcISA::FloatRegIndex::F52},
    {"53", SparcISA::FloatRegIndex::F53},
    {"54", SparcISA::FloatRegIndex::F54},
    {"55", SparcISA::FloatRegIndex::F55},
    {"56", SparcISA::FloatRegIndex::F56},
    {"57", SparcISA::FloatRegIndex::F57},
    {"58", SparcISA::FloatRegIndex::F58},
    {"59", SparcISA::FloatRegIndex::F59},

    {"60", SparcISA::FloatRegIndex::F60},
    {"61", SparcISA::FloatRegIndex::F61},
    {"62", SparcISA::FloatRegIndex::F62},
    {"63", SparcISA::FloatRegIndex::F63}
};
static std::map<std::string, int> SPARCDoubleRegConverter = 
{
    {"d0", SparcISA::FloatRegIndex::F0},
    {"d2", SparcISA::FloatRegIndex::F2},
    {"d4", SparcISA::FloatRegIndex::F4},
    {"d6", SparcISA::FloatRegIndex::F6},
    {"d8", SparcISA::FloatRegIndex::F8},

    {"d20", SparcISA::FloatRegIndex::F20},
    {"d22", SparcISA::FloatRegIndex::F22},
    {"d24", SparcISA::FloatRegIndex::F24},
    {"d26", SparcISA::FloatRegIndex::F26},
    {"d28", SparcISA::FloatRegIndex::F28},

    {"d30", SparcISA::FloatRegIndex::F30},
    {"d32", SparcISA::FloatRegIndex::F32},
    {"d34", SparcISA::FloatRegIndex::F34},
    {"d36", SparcISA::FloatRegIndex::F36},
    {"d38", SparcISA::FloatRegIndex::F38},

    {"d40", SparcISA::FloatRegIndex::F40},
    {"d42", SparcISA::FloatRegIndex::F42},
    {"d44", SparcISA::FloatRegIndex::F44},
    {"d46", SparcISA::FloatRegIndex::F46},
    {"d48", SparcISA::FloatRegIndex::F48},

    {"d50", SparcISA::FloatRegIndex::F50},
    {"d52", SparcISA::FloatRegIndex::F52},
    {"d54", SparcISA::FloatRegIndex::F54},
    {"d56", SparcISA::FloatRegIndex::F56},
    {"d58", SparcISA::FloatRegIndex::F58},

    {"d60", SparcISA::FloatRegIndex::F60},
    {"d62", SparcISA::FloatRegIndex::F62},

// an alternative to using exact index instead

    {"0", SparcISA::FloatRegIndex::F0},
    {"2", SparcISA::FloatRegIndex::F2},
    {"4", SparcISA::FloatRegIndex::F4},
    {"6", SparcISA::FloatRegIndex::F6},
    {"8", SparcISA::FloatRegIndex::F8},

    {"20", SparcISA::FloatRegIndex::F20},
    {"22", SparcISA::FloatRegIndex::F22},
    {"24", SparcISA::FloatRegIndex::F24},
    {"26", SparcISA::FloatRegIndex::F26},
    {"28", SparcISA::FloatRegIndex::F28},

    {"30", SparcISA::FloatRegIndex::F30},
    {"32", SparcISA::FloatRegIndex::F32},
    {"34", SparcISA::FloatRegIndex::F34},
    {"36", SparcISA::FloatRegIndex::F36},
    {"38", SparcISA::FloatRegIndex::F38},

    {"40", SparcISA::FloatRegIndex::F40},
    {"42", SparcISA::FloatRegIndex::F42},
    {"44", SparcISA::FloatRegIndex::F44},
    {"46", SparcISA::FloatRegIndex::F46},
    {"48", SparcISA::FloatRegIndex::F48},

    {"50", SparcISA::FloatRegIndex::F50},
    {"52", SparcISA::FloatRegIndex::F52},
    {"54", SparcISA::FloatRegIndex::F54},
    {"56", SparcISA::FloatRegIndex::F56},
    {"58", SparcISA::FloatRegIndex::F58},

    {"60", SparcISA::FloatRegIndex::F60},
    {"62", SparcISA::FloatRegIndex::F62},
};

// convert string to correct register index
static std::map<std::string, int> x86IntRegConverter =
{
    {"rax", X86ISA::IntRegIndex::INTREG_RAX},
    {"eax", X86ISA::IntRegIndex::INTREG_EAX},
    {"ax", X86ISA::IntRegIndex::INTREG_AX},
    {"al", X86ISA::IntRegIndex::INTREG_AL},

    {"rcx", X86ISA::IntRegIndex::INTREG_RCX},
    {"ecx", X86ISA::IntRegIndex::INTREG_ECX},
    {"cx", X86ISA::IntRegIndex::INTREG_CX},
    {"cl", X86ISA::IntRegIndex::INTREG_CL},

    {"rdx", X86ISA::IntRegIndex::INTREG_RDX},
    {"edx", X86ISA::IntRegIndex::INTREG_EDX},
    {"dx", X86ISA::IntRegIndex::INTREG_DX},
    {"dl", X86ISA::IntRegIndex::INTREG_DL},

    {"rbx", X86ISA::IntRegIndex::INTREG_RBX},
    {"ebx", X86ISA::IntRegIndex::INTREG_EBX},
    {"bx", X86ISA::IntRegIndex::INTREG_BX},
    {"bl", X86ISA::IntRegIndex::INTREG_BL},

    {"rsp", X86ISA::IntRegIndex::INTREG_RSP},
    {"esp", X86ISA::IntRegIndex::INTREG_ESP},
    {"sp", X86ISA::IntRegIndex::INTREG_SP},
    {"spl", X86ISA::IntRegIndex::INTREG_SPL},
    {"ah", X86ISA::IntRegIndex::INTREG_AH},

    {"rbp", X86ISA::IntRegIndex::INTREG_RBP},
    {"ebp", X86ISA::IntRegIndex::INTREG_EBP},
    {"bp", X86ISA::IntRegIndex::INTREG_BP},
    {"bpl", X86ISA::IntRegIndex::INTREG_BPL},
    {"ch", X86ISA::IntRegIndex::INTREG_CH},

    {"rsi", X86ISA::IntRegIndex::INTREG_RSI},
    {"esi", X86ISA::IntRegIndex::INTREG_ESI},
    {"si", X86ISA::IntRegIndex::INTREG_SI},
    {"sil", X86ISA::IntRegIndex::INTREG_SIL},
    {"dh", X86ISA::IntRegIndex::INTREG_DH},

    {"rdi", X86ISA::IntRegIndex::INTREG_RDI},
    {"edi", X86ISA::IntRegIndex::INTREG_EDI},
    {"di", X86ISA::IntRegIndex::INTREG_DI},
    {"dil", X86ISA::IntRegIndex::INTREG_DIL},
    {"bh", X86ISA::IntRegIndex::INTREG_BH},

    {"r8", X86ISA::IntRegIndex::INTREG_R8},
    {"r9", X86ISA::IntRegIndex::INTREG_R9},
    {"r10", X86ISA::IntRegIndex::INTREG_R10},
    {"r11", X86ISA::IntRegIndex::INTREG_R11},
    {"r12", X86ISA::IntRegIndex::INTREG_R12},
    {"r13", X86ISA::IntRegIndex::INTREG_R13},
    {"r14", X86ISA::IntRegIndex::INTREG_R14},
    {"r15", X86ISA::IntRegIndex::INTREG_R15}
};

// each FP register may need different bit flips depending on which
// data we are accessing. An example is "movapd %xmm1,%xmm2" 
// that moves xmm1_high->xmm2_high, and xmm1_low->xmm2_low
static std::map<std::string, int> x86FloatRegConverter =
{
    {"fpr0", X86ISA::FloatRegIndex::FLOATREG_FPR0},
    {"fpr1", X86ISA::FloatRegIndex::FLOATREG_FPR1},
    {"fpr2", X86ISA::FloatRegIndex::FLOATREG_FPR2},
    {"fpr3", X86ISA::FloatRegIndex::FLOATREG_FPR3},
    {"fpr4", X86ISA::FloatRegIndex::FLOATREG_FPR4},
    {"fpr5", X86ISA::FloatRegIndex::FLOATREG_FPR5},
    {"fpr6", X86ISA::FloatRegIndex::FLOATREG_FPR7},
    {"fpr7", X86ISA::FloatRegIndex::FLOATREG_FPR7},

    {"xmm0", X86ISA::FloatRegIndex::FLOATREG_XMM0_LOW},
    {"xmm0_low", X86ISA::FloatRegIndex::FLOATREG_XMM0_LOW},
    {"xmm0_high", X86ISA::FloatRegIndex::FLOATREG_XMM0_HIGH},

    {"xmm1", X86ISA::FloatRegIndex::FLOATREG_XMM1_LOW},
    {"xmm1_low", X86ISA::FloatRegIndex::FLOATREG_XMM1_LOW},
    {"xmm1_high", X86ISA::FloatRegIndex::FLOATREG_XMM1_HIGH},

    {"xmm2", X86ISA::FloatRegIndex::FLOATREG_XMM2_LOW},
    {"xmm2_low", X86ISA::FloatRegIndex::FLOATREG_XMM2_LOW},
    {"xmm2_high", X86ISA::FloatRegIndex::FLOATREG_XMM2_HIGH},

    {"xmm3", X86ISA::FloatRegIndex::FLOATREG_XMM3_LOW},
    {"xmm3_low", X86ISA::FloatRegIndex::FLOATREG_XMM3_LOW},
    {"xmm3_high", X86ISA::FloatRegIndex::FLOATREG_XMM3_HIGH},

    {"xmm4", X86ISA::FloatRegIndex::FLOATREG_XMM4_LOW},
    {"xmm4_low", X86ISA::FloatRegIndex::FLOATREG_XMM4_LOW},
    {"xmm4_high", X86ISA::FloatRegIndex::FLOATREG_XMM4_HIGH},

    {"xmm5", X86ISA::FloatRegIndex::FLOATREG_XMM5_LOW},
    {"xmm5_low", X86ISA::FloatRegIndex::FLOATREG_XMM5_LOW},
    {"xmm5_high", X86ISA::FloatRegIndex::FLOATREG_XMM5_HIGH},

    {"xmm6", X86ISA::FloatRegIndex::FLOATREG_XMM6_LOW},
    {"xmm6_low", X86ISA::FloatRegIndex::FLOATREG_XMM6_LOW},
    {"xmm6_high", X86ISA::FloatRegIndex::FLOATREG_XMM6_HIGH},

    {"xmm7", X86ISA::FloatRegIndex::FLOATREG_XMM7_LOW},
    {"xmm7_low", X86ISA::FloatRegIndex::FLOATREG_XMM7_LOW},
    {"xmm7_high", X86ISA::FloatRegIndex::FLOATREG_XMM7_HIGH},

    {"xmm8", X86ISA::FloatRegIndex::FLOATREG_XMM8_LOW},
    {"xmm8_low", X86ISA::FloatRegIndex::FLOATREG_XMM8_LOW},
    {"xmm8_high", X86ISA::FloatRegIndex::FLOATREG_XMM8_HIGH},

    {"xmm9", X86ISA::FloatRegIndex::FLOATREG_XMM9_LOW},
    {"xmm9_low", X86ISA::FloatRegIndex::FLOATREG_XMM9_LOW},
    {"xmm9_high", X86ISA::FloatRegIndex::FLOATREG_XMM9_HIGH},

    {"xmm10", X86ISA::FloatRegIndex::FLOATREG_XMM10_LOW},
    {"xmm10_low", X86ISA::FloatRegIndex::FLOATREG_XMM10_LOW},
    {"xmm10_high", X86ISA::FloatRegIndex::FLOATREG_XMM10_HIGH},

    {"xmm11", X86ISA::FloatRegIndex::FLOATREG_XMM11_LOW},
    {"xmm11_low", X86ISA::FloatRegIndex::FLOATREG_XMM11_LOW},
    {"xmm11_high", X86ISA::FloatRegIndex::FLOATREG_XMM11_HIGH},
    
    {"xmm12", X86ISA::FloatRegIndex::FLOATREG_XMM12_LOW},
    {"xmm12_low", X86ISA::FloatRegIndex::FLOATREG_XMM12_LOW},
    {"xmm12_high", X86ISA::FloatRegIndex::FLOATREG_XMM12_HIGH},

    {"xmm13", X86ISA::FloatRegIndex::FLOATREG_XMM13_LOW},
    {"xmm13_low", X86ISA::FloatRegIndex::FLOATREG_XMM13_LOW},
    {"xmm13_high", X86ISA::FloatRegIndex::FLOATREG_XMM13_HIGH},

    {"xmm14", X86ISA::FloatRegIndex::FLOATREG_XMM14_LOW},
    {"xmm14_low", X86ISA::FloatRegIndex::FLOATREG_XMM14_LOW},
    {"xmm14_high", X86ISA::FloatRegIndex::FLOATREG_XMM14_HIGH},

    {"xmm15", X86ISA::FloatRegIndex::FLOATREG_XMM15_LOW},
    {"xmm15_low", X86ISA::FloatRegIndex::FLOATREG_XMM15_LOW},
    {"xmm15_high", X86ISA::FloatRegIndex::FLOATREG_XMM15_HIGH}
};

static std::vector<std::map<std::string, int>> x86Table = 
{
    x86IntRegConverter,
    x86FloatRegConverter   
};

static std::vector<std::map<std::string, int>> SPARCTable = 
{
    SPARCIntRegConverter,
    SPARCFloatRegConverter,
    SPARCDoubleRegConverter
};

static std::map<std::string, std::vector<std::map<std::string, int>>> archMap = 
{
    {"x86", x86Table},
    {"SPARC", SPARCTable}
};

// TODO: add PC (thread->instAddr())
class FI
{
  protected:
    std::string ISA;
    Tick when;
    ThreadContext* thread;
  public:
    FI(ThreadContext* _thread, Tick _when, std::string _ISA)
        : ISA(_ISA), when(_when), thread(_thread)
    { }
    void FlipBit(Tick _injTick, int injR, int injBit, int regType);

};

class Injector : public SimObject
{    
  public:
    std::string ISA;
    std::string injPC;
    int injBit;
    Tick injTick;
    std::string injReg;
    int regType;
    int srcDest;
    Tick timeoutVal; // = 10000000000; // test timeout
    std::string goldenFile;

    std::vector<std::string> goldenTrace;

    Injector(InjectorParams *p);
    void PerformFI(ThreadContext* _thread, Tick _when,
                   Tick _injTick, std::string ISA, std::string desiredR, int injBit, int regType);
    void trackState(std::string faultyTrace, std::string goldenTrace);
};

}   // end namespace




#endif
