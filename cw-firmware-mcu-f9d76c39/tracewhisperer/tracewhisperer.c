#include <stdio.h>
#include "hal.h"
#include "simpleserial.h"
#include "tracewhisperer.h"

uint8_t pcsamp_enable;

#if SS_VER==SS_VER_1_1 || SS_VER==SS_VER_2_1
uint8_t setreg(uint8_t* x, uint8_t len)
#elif SS_VER==SS_VER_1_0
uint8_t setreg(uint8_t* x, uint32_t len)
#endif
{
        uint32_t val;
        val = x[4] + (x[3] << 8) + (x[2] << 16) + (x[1] << 24);
// Must match capture/trace/TraceWhisperer.py:
//0:  DWT->CTRL
//1:  DWT->COMP0
//2:  DWT->COMP1
//3:  ETM->CR
//4:  ETM->TESSEICR
//5:  ETM->TEEVR
//6:  ETM->TECR1
//7:  ETM->TRACEIDR
//8:  TPIU->ACPR
//9:  TPIU->SPPR
//10: TPIU->FFCR
//11: TPIU->CSPSR
//12: ITM->TCR
        if       (x[0] == 0)    {DWT->CTRL = val;}
        else if  (x[0] == 1)    {DWT->COMP0 = val;}
        else if  (x[0] == 2)    {DWT->COMP1 = val;}
        else if  (x[0] == 3)    {ETM_SetupMode(); ETM->CR = val; ETM_TraceMode();}
        else if  (x[0] == 4)    {ETM_SetupMode(); ETM->TESSEICR = val; ETM_TraceMode();}
        else if  (x[0] == 5)    {ETM_SetupMode(); ETM->TEEVR    = val; ETM_TraceMode();}
        else if  (x[0] == 6)    {ETM_SetupMode(); ETM->TECR1    = val; ETM_TraceMode();}
        else if  (x[0] == 7)    {ETM_SetupMode(); ETM->TRACEIDR = val; ETM_TraceMode();}
        else if  (x[0] == 8)    {TPIU->ACPR    = val;}
        else if  (x[0] == 9)    {TPIU->SPPR    = val;}
        else if  (x[0] == 10)   {TPIU->FFCR    = val;}
        else if  (x[0] == 11)   {TPIU->CSPSR   = val;}
        else if  (x[0] == 12)   {ITM->TCR     = val;}

	return 0x00;
}


#if SS_VER==SS_VER_1_1 || SS_VER==SS_VER_2_1
uint8_t getreg(uint8_t* x, uint8_t len)
#elif SS_VER==SS_VER_1_0
uint8_t getreg(uint8_t* x, uint32_t len)
#endif
{
        uint32_t val;
        if       (x[0] == 0)    {val = DWT->CTRL;}
        else if  (x[0] == 1)    {val = DWT->COMP0;}
        else if  (x[0] == 2)    {val = DWT->COMP1 ;}
        else if  (x[0] == 3)    {val = ETM->CR;}
        else if  (x[0] == 4)    {val = ETM->TESSEICR;}
        else if  (x[0] == 5)    {val = ETM->TEEVR;}
        else if  (x[0] == 6)    {val = ETM->TECR1;}
        else if  (x[0] == 7)    {val = ETM->TRACEIDR;}
        else if  (x[0] == 8)    {val = TPIU->ACPR;}
        else if  (x[0] == 9)    {val = TPIU->SPPR;}
        else if  (x[0] == 10)   {val = TPIU->FFCR;}
        else if  (x[0] == 11)   {val = TPIU->CSPSR;}
        else if  (x[0] == 12)   {val = ITM->TCR;}
        else {val = 0;}

        x[3] = val & 0xff;
        x[2] = (val >> 8) & 0xff;
        x[1] = (val >> 16) & 0xff;
        x[0] = (val >> 24) & 0xff;
#if SS_VER==SS_VER_1_1 || SS_VER==SS_VER_2_1
	simpleserial_put('r', 4, x);
#elif SS_VER==SS_VER_1_0
	for (int i = 0; i < 4; i++)
		printf("%02x", x[i]);
	printf("\n");
#endif
	return 0x00;
}


// Print a given string to ITM with 8-bit writes.
static void ITM_Print(int port, const char *p)
{
    if ((ITM->TCR & ITM_TCR_ITMENA_Msk) && (ITM->TER & (1UL << port)))
    {
        while (*p)
        {
            while (ITM->PORT[port].u32 == 0);
            ITM->PORT[port].u8 = *p++;
        }
        hal_send_str("ITM alive!\n");
    }
    else {hal_send_str("Couldn't print!\n");}
}


void enable_trace(void)
{
    // Enable SWO pin (not required on K82)
    #if (HAL_TYPE == HAL_stm32f3) || (HAL_TYPE == HAL_stm32f4)
       DBGMCU->CR |= DBGMCU_CR_TRACE_IOEN_Msk;
    #endif

    // Configure TPIU
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk; // Enable access to registers
    TPIU->ACPR = 0; // SWO trace baud rate = cpu clock / (ACPR+1)

    #if (HAL_TYPE == HAL_stm32f3) || (HAL_TYPE == HAL_stm32f4) || (HAL_TYPE == HAL_sam4s)
       TPIU->SPPR = 2; // default to SWO with NRZ encoding
       //TPIU->SPPR = 1; // SWO with Manchester encoding
    #else
       TPIU->SPPR = 0; // default to parallel trace mode
    #endif

    TPIU->FFCR = 0x102; // packet framing enabled
    //TPIU->FFCR = 0x100; // no framing: for DWT/ITM only, no ETM
    TPIU->CSPSR =0x00000008; // 4 trace lanes

    // Configure ITM:
    ITM->LAR = 0xC5ACCE55;
    ITM->TCR = (1 << ITM_TCR_TRACEBUSID_Pos) // Trace bus ID for TPIU
             | (1 << ITM_TCR_DWTENA_Pos) // Enable events from DWT
             | (0 << ITM_TCR_SYNCENA_Pos) // Disable sync packets!
             | (1 << ITM_TCR_ITMENA_Pos); // Main enable for ITM
    ITM->TER = 0xFFFFFFFF; // Enable all stimulus ports
    ITM->TPR = 0x00000000; // allow unpriviledged access

    // Configure DWT:
    DWT->CTRL = (0xf << DWT_CTRL_POSTINIT_Pos);// countdown counter for PC sampling, must be written
                                               // before enabling PC sampling
    DWT->CTRL |=(1 << DWT_CTRL_CYCTAP_Pos)     // Prescaler for PC sampling: 0 = x32, 1 = x512
              | (8 << DWT_CTRL_POSTPRESET_Pos) // PC sampling postscaler
              | (0 << DWT_CTRL_PCSAMPLENA_Pos) // disable PC sampling
              | (1 << DWT_CTRL_SYNCTAP_Pos)    // sync packets every 16M cycles
              | (0 << DWT_CTRL_EXCTRCENA_Pos)  // disable exception trace
              | (1 << DWT_CTRL_CYCCNTENA_Pos); // enable cycle counter

    // Configure DWT PC comparator 0:
    DWT->COMP0 = 0x00001d60; // AES subbytes
    DWT->MASK0 = 0;
    DWT->FUNCTION0 = (0 << DWT_FUNCTION_DATAVMATCH_Pos) // address match
                   | (0 << DWT_FUNCTION_CYCMATCH_Pos)
                   | (0 << DWT_FUNCTION_EMITRANGE_Pos)
                   | (8 << DWT_FUNCTION_FUNCTION_Pos); // Iaddr CMPMATCH event

    // Configure DWT PC comparator 1:
    DWT->COMP1 = 0x00001d68; // AES mixcolumns
    DWT->MASK1 = 0;
    DWT->FUNCTION1 = (0 << DWT_FUNCTION_DATAVMATCH_Pos) // address match
                   | (0 << DWT_FUNCTION_CYCMATCH_Pos)
                   | (0 << DWT_FUNCTION_EMITRANGE_Pos)
                   | (8 << DWT_FUNCTION_FUNCTION_Pos); // Iaddr CMPMATCH event


    // Configure ETM:
    ETM->LAR = 0xC5ACCE55;
    ETM_SetupMode();
    ETM->CR = ETM_CR_ETMEN; // Enable ETM output port
    ETM->TRACEIDR = 1; // Trace bus ID for TPIU
    ETM->FFLR = 0; // Stall processor when FIFO is full
    ETM->TEEVR = 0x000150a0;    // EmbeddedICE comparator 0 or 1 (DWT->COMP0 or DWT->COMP1)
    //ETM->TEEVR = 0x00000020;    // EmbeddedICE comparator 0 only
    //ETM->TEEVR = 0x00000021;    // EmbeddedICE comparator 1 only
    ETM->TESSEICR = 0xf; // set EmbeddedICE watchpoint 0 as a TraceEnable start resource.
    ETM->TECR1 = 0; // tracing is unaffected by the trace start/stop logic
    ETM_TraceMode();
}


#if SS_VER==SS_VER_1_1 || SS_VER==SS_VER_2_1
uint8_t test_itm(uint8_t* x, uint8_t len)
#elif SS_VER==SS_VER_1_0
uint8_t test_itm(uint8_t* x, uint32_t len)
#endif
{
    ITM_Print(x[0], "ITM alive!\n");
    return 0x00;
}

#if SS_VER==SS_VER_1_1 || SS_VER==SS_VER_2_1
uint8_t set_pcsample_params(uint8_t* x, uint8_t len)
#elif SS_VER==SS_VER_1_0
uint8_t set_pcsample_params(uint8_t* x, uint32_t len)
#endif
{
    uint8_t postinit;
    uint8_t postreset;
    uint8_t cyctap;
    pcsamp_enable = x[0] & 1;
    cyctap = x[1] & 1;
    postinit  = x[2] & 0xf;
    postreset = x[3] & 0xf;

    // must clear everything before updating postinit field:
    DWT->CTRL = 0;
    // then update postinit:
    DWT->CTRL = (postinit << DWT_CTRL_POSTINIT_Pos);
    // then update the reset, but don't turn on PC sampling yet;
    // that will be handled in trigger_high_pcsamp
    DWT->CTRL = (cyctap << DWT_CTRL_CYCTAP_Pos)
              | (postreset << DWT_CTRL_POSTPRESET_Pos)
              | (postinit << DWT_CTRL_POSTINIT_Pos)
              | (1 << DWT_CTRL_SYNCTAP_Pos)
              | (1 << DWT_CTRL_CYCCNTENA_Pos);
#if SS_VER==SS_VER_1_1 || SS_VER==SS_VER_2_1
    simpleserial_put('r', 4, x);
#elif SS_VER==SS_VER_1_0
    for (int i = 0; i < 4; i++)
	printf("%02x", x[i]);
    printf("\n");
#endif

    return 0x00;
}

// in order for PC sample packets to be easily parsed, PC sampling must
// begin *after* we start capturing trace data
void trigger_high_pcsamp(void)
{
    if (pcsamp_enable == 1)
    {
        DWT->CTRL |= (1 << DWT_CTRL_PCSAMPLENA_Pos); // enable PC sampling
    }
    trigger_high();
}


void trigger_low_pcsamp(void)
{
    trigger_low();
    DWT->CTRL &= ~(1 << DWT_CTRL_PCSAMPLENA_Pos); // disable PC sampling
}


#if SS_VER==SS_VER_1_1 || SS_VER==SS_VER_2_1
__attribute__((weak)) uint8_t info(uint8_t* x, uint8_t len)
#elif SS_VER==SS_VER_1_0
__attribute__((weak)) uint8_t info(uint8_t* x, uint32_t len)
#endif
{
	hal_send_str("Compiled on ");
	hal_send_str(__DATE__);
	hal_send_str(", ");
	hal_send_str(__TIME__);
	hal_send_str("\n");
	return 0x00;
}
