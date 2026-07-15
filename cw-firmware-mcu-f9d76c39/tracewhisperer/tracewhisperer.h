#include <stdint.h>

#include "arm_etm.h"

#ifndef TRACEWHISPERER_H
#define TRACEWHISPERER_H

#if SS_VER==SS_VER_1_1 || SS_VER==SS_VER_2_1
/* simpleserial_addcmd('s', 5, setreg);
   Used in '_set' */
uint8_t setreg(uint8_t* x, uint8_t len);

/* simpleserial_addcmd('g', 5, getreg);
   Used in '_get' */
uint8_t getreg(uint8_t* x, uint8_t len);

/* simpleserial_addcmd('t', 1, test_itm);
   Used in 'test_itm' */
uint8_t test_itm(uint8_t* x, uint8_t len);

/* simpleserial_addcmd('c', 4, set_pcsample_params);
   Used in 'set_periodic_pc_sampling' */
uint8_t set_pcsample_params(uint8_t* x, uint8_t len);

/* uint8_t info(uint8_t* x, uint8_t len);
   Used in 'info' */
uint8_t info(uint8_t* x, uint8_t len);

#elif SS_VER==SS_VER_1_0
/* simpleserial_addcmd('s', setreg);
   Used in '_set' */
uint8_t setreg(uint8_t* x, uint32_t len);

/* simpleserial_addcmd('g', getreg);
   Used in '_get' */
uint8_t getreg(uint8_t* x, uint32_t len);

void enable_trace(void);

/* simpleserial_addcmd('t', test_itm);
   Used in 'test_itm' */
uint8_t test_itm(uint8_t* x, uint32_t len);

/* simpleserial_addcmd('c', set_pcsample_params);
   Used in 'set_periodic_pc_sampling' */
uint8_t set_pcsample_params(uint8_t* x, uint32_t len);

#endif

void enable_trace(void);
void trigger_high_pcsamp(void);
void trigger_low_pcsamp(void);

#endif
