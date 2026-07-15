// SPDX-License-Identifier: Apache-2.0 or CC0-1.0
#ifdef __cplusplus
extern "C" {
#endif

#include <hal.h>
#include <CMSDK_CM4.h>
#include <stdio.h>
#include <unistd.h>
#include <errno.h>

#define BAUD 38400

/* Default clock on the MPS2 boards seems to be 25MHz */
#ifndef SYSTEM_CLOCK
#define SYSTEM_CLOCK 25000000UL
#endif

/* The startup file calls a SystemInit function. */
void SystemInit(void)
{
  /* Enable the FPU */
  SCB->CPACR |= ((3UL << 10 * 2) |               /* set CP10 Full Access */
                 (3UL << 11 * 2));               /* set CP11 Full Access */
  /* Enable UART */
  /* TODO: Validate this on a *real* MPS2 board (works in QEMU) */
  CMSDK_GPIO0->ALTFUNCSET |= 1u;
  CMSDK_GPIO0->ALTFUNCSET |= 2u;
  CMSDK_UART0->BAUDDIV = SYSTEM_CLOCK / BAUD;
  CMSDK_UART0->CTRL |= 1 << CMSDK_UART_CTRL_RXEN_Pos;
  CMSDK_UART0->CTRL |= 1 << CMSDK_UART_CTRL_TXEN_Pos;
  /* Enable SysTick Timer */
  SysTick->LOAD = 0xFFFFFFu;
  NVIC_SetPriority(SysTick_IRQn, (1UL << __NVIC_PRIO_BITS) - 1UL);
  NVIC_EnableIRQ(SysTick_IRQn);
  SysTick->VAL = 0UL;
  SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk | SysTick_CTRL_TICKINT_Msk | SysTick_CTRL_ENABLE_Msk;
}

static volatile unsigned long long overflowcnt = 0;

/* SysTick Interrupt */
void SysTick_Handler(void)
{
  ++overflowcnt;
}

uint64_t HAL_CYCCNT(void)	/* old: hal_get_time */
{
  while (1) {
    unsigned long long before = overflowcnt;
    unsigned long long result = (before + 1) * 16777216llu - SysTick->VAL;
    if (overflowcnt == before) {
      return result;
    }
  }
}

void putch(char c)  /* origin: static inline void uart_putc(int c) */
{
	while (CMSDK_UART0->STATE & CMSDK_UART_STATE_TXBF_Msk)
		;
	CMSDK_UART0->DATA = c & 0xFFu;
}

/* _write prototype is in /usr/arm-none-eabi/include/sys/unistd.h */
_READ_WRITE_RETURN_TYPE _write (int __fd, const void *__buf, size_t __nbyte)
{
	if (__fd != STDOUT_FILENO && __fd != STDERR_FILENO) {
		errno = EBADF;
		return -1;
	}

	const uint8_t *pData = (const uint8_t *)__buf;
	size_t written = 0;

	/* Send each byte through UART */
	while (written < __nbyte) {
		putch((char)pData[written]);
		written++;
	}

	/* Return number of bytes successfully written */
	return (_READ_WRITE_RETURN_TYPE)written;
}

#if !defined(NO_SEMIHOSTING_EXIT)
// TODO(dsprenkels) Currently, we only exit the QEMU host when a the program
// exists sucessfully.  We should also populate some interrupts handlers that
// occur on errors and/or other exception.

// These two syscall values are used at the end of the program, when we want
// to tell the QEMU host that we are done.  I took them from
// <https://github.com/rust-embedded/cortex-m-semihosting/blob/8ab74cdb8c9ab669ded328072447ea6f6054ffe6/src/debug.rs#L25-L50>.
static const uint32_t REPORT_EXCEPTION = 0x18;
static const uint32_t ApplicationExit = 0x20026;

// Do a system call towards QEMU or the debugger.
static uint32_t semihosting_syscall(uint32_t nr, const uint32_t arg) {
	__asm__ volatile (
		"mov r0, %[nr]\n"
		"mov r1, %[arg]\n"
		"bkpt 0xAB\n"
		"mov %[nr], r0\n"
	: [nr] "+r" (nr) : [arg] "r" (arg) : "0", "1");
	return nr;
}

// Register a destructor that will call qemu telling them that the program
// has exited successfully.
static void __attribute__ ((destructor)) semihosting_exit(void) {
	semihosting_syscall(REPORT_EXCEPTION, ApplicationExit);
}

void NMI_Handler(void) {
  printf("NMI_Handler");
  semihosting_syscall(REPORT_EXCEPTION, ApplicationExit);
}

void HardFault_Handler(void) {
  printf("HardFault_Handler");
  semihosting_syscall(REPORT_EXCEPTION, ApplicationExit);
}

void MemManage_Handler(void) {
  printf("MemManage_Handler");
  semihosting_syscall(REPORT_EXCEPTION, ApplicationExit);
}

void BusFault_Handler(void) {
  printf("BusFault_Handler");
  semihosting_syscall(REPORT_EXCEPTION, ApplicationExit);
}

void UsageFault_Handler(void) {
  printf("UsageFault_Handler");
  semihosting_syscall(REPORT_EXCEPTION, ApplicationExit);
}

void SVC_Handler(void) {
  printf("SVC_Handler");
  semihosting_syscall(REPORT_EXCEPTION, ApplicationExit);
}

void DebugMon_Handler(void) {
  printf("DebugMon_Handler");
  semihosting_syscall(REPORT_EXCEPTION, ApplicationExit);
}

void PendSV_Handler(void) {
  printf("PendSV_Handler");
  semihosting_syscall(REPORT_EXCEPTION, ApplicationExit);
}

void Default_Handler(void) {
  semihosting_syscall(REPORT_EXCEPTION, ApplicationExit);
}

#endif /* !defined(NO_SEMIHOSTING_EXIT) */

#ifdef __cplusplus
}
#endif
