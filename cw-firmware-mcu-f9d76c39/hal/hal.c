/*
    This file is part of the ChipWhisperer Example Targets
    Copyright (C) 2012-2015 NewAE Technology Inc.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifdef __cplusplus
extern "C" {
#endif

#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/stat.h>
/* #include <reent.h> */
#include "hal.h"

__attribute__((weak)) void led_ok(unsigned int status)
{
}

__attribute__((weak)) void led_error(unsigned int status)
{
}

#ifdef PLATFORM_ARM

/* void hal_setup(const enum clock_mode clock) */
void hal_setup()
{
#if HAL_TYPE != HAL_mps2
	platform_init();
	init_uart();
	setvbuf(stdout, NULL, _IONBF, 0);  // optional: line-buffered
	setvbuf(stderr, NULL, _IONBF, 0);
	trigger_setup();
#endif
}

void hal_send_str(const char *in)
{
	const char *cur = in;
	while (*cur)
		putch(*(cur++));
}

/* End of BSS is where the heap starts (defined in the linker script) */
extern char __end__;
extern char __heap_limit;
static char *heap_end;
extern char __heap_start__;

#if 1
void *__wrap__sbrk(int incr)
{
	if (heap_end == 0)
		heap_end = &__end__;

	char *prev = heap_end;
	char *next = heap_end + incr;

	if (next >= (char *)&__heap_limit) {
		errno = ENOMEM;
		return (void *)-1; /* let malloc/calloc return NULL */
	}
	/* heap_end += incr; */
	heap_end = next;

	/* return (void *)prev; */
	return prev;
}
#endif

#if 0
  .heap (NOLOAD) :
{
  . = ALIGN(8);
  __heap_start__ = .;
  . = . + 160K - 16;  /* Use almost all CCM for heap */
  __heap_limit = .;
  . = ALIGN(8);
} >CCM

void *__wrap__sbrk(int incr)
{
	if (heap_end == 0)
		heap_end = &__heap_start__;  /* Start from CCM heap */

	char *prev = heap_end;
	char *next = heap_end + incr;

	if (next >= (char *)&__heap_limit) {
		errno = ENOMEM;
		return (void *)-1;
	}

	heap_end = next;
	return prev;
}
#endif

uint32_t hal_get_stack_size(void)
{
	/* return u32 b.c. in Cortex M4, sizeof(char *) = 4 */
	register char *cur_stack;
	__asm__ volatile("mov %0, sp" : "=r"(cur_stack));
	return cur_stack - heap_end;
}

const uint32_t stackpattern = 0xDEADBEEFlu;

static void *last_sp = NULL;

void hal_spraystack(void)
{
	char *_heap_end = heap_end;
	asm volatile("mov %0, sp\n"
		     ".L%=:\n\t"
		     "str %2, [%1], #4\n\t"
		     "cmp %1, %0\n\t"
		     "blt .L%=\n\t"
		     : "+r"(last_sp), "+r"(_heap_end)
		     : "r"(stackpattern)
		     : "cc", "memory");
}

size_t hal_checkstack(void)
{
	size_t result = 0;
	asm volatile("sub %0, %1, %2\n"
		     ".L%=:\n\t"
		     "ldr ip, [%2], #4\n\t"
		     "cmp ip, %3\n\t"
		     "ite eq\n\t"
		     "subeq %0, #4\n\t"
		     "bne .LE%=\n\t"
		     "cmp %2, %1\n\t"
		     "blt .L%=\n\t"
		     ".LE%=:\n"
		     : "+r"(result)
		     : "r"(last_sp), "r"(heap_end), "r"(stackpattern)
		     : "ip", "cc");
	return result;
}

/*****************************************************************************/
/*                define syscall stubs (pseudo "system call")                */
/*****************************************************************************/

#if defined(STM32F4)

extern UART_HandleTypeDef UartHandle;

/* _read prototype is in /usr/arm-none-eabi/include/sys/unistd.h */
_READ_WRITE_RETURN_TYPE _read (int __fd, void *__buf, size_t __nbyte)
{
	if (__fd != STDIN_FILENO) {
		errno = EBADF;
		return -1;
	}

	uint8_t *pData = (uint8_t *)__buf;
	size_t bytes_read = 0;

	/* Read character by character to support line buffering */
	while (bytes_read < __nbyte) {
		if (HAL_UART_Receive(&UartHandle, &pData[bytes_read], 1,
				     HAL_MAX_DELAY) != HAL_OK) {
			if (bytes_read > 0) {
				break;  /* Return partial read */
			}
			errno = EIO;
			return -1;
		}
		bytes_read++;
		/* Stop at newline for line-buffered input */
		if (pData[bytes_read - 1] == '\n')
			break;
	}

	return (_READ_WRITE_RETURN_TYPE)bytes_read;
}

/* _write prototype is in /usr/arm-none-eabi/include/sys/unistd.h */
_READ_WRITE_RETURN_TYPE _write (int __fd, const void *__buf, size_t __nbyte)
{
	if (__fd != STDOUT_FILENO && __fd != STDERR_FILENO) {
		errno = EBADF;
		return -1;
	}

	/* HAL_UART_Transmit takes uint16_t length; chunk if len > 65535 */
	uint8_t *pData = (uint8_t *)__buf;
	size_t remaining = __nbyte;
	while (remaining > 0) {
		uint16_t chunk = (remaining > 0xffff) ?
			0xffff : (uint16_t)remaining;
		if (HAL_UART_Transmit(&UartHandle, pData, chunk,
				      HAL_MAX_DELAY) != HAL_OK) {
			errno = EIO;
			return -1;
		}
		pData += chunk;
		remaining -= chunk;
	}
	/* If success, should return the original full length */
	return (_READ_WRITE_RETURN_TYPE)__nbyte;
}

/* _isatty prototype is in /usr/arm-none-eabi/include/sys/unistd.h */
int _isatty(int __fildes)
{
	return (__fildes == STDOUT_FILENO ||
		__fildes == STDERR_FILENO) ?
		1 : 0;
}

/* _fstat prototype is in /usr/arm-none-eabi/include/sys/stat.h */
int _fstat(int fd, struct stat *st)
{
	if (!st) {
		errno = EINVAL;
		return -1;
	}
	if (fd == STDOUT_FILENO || fd == STDERR_FILENO) {
		st->st_mode = S_IFCHR; /* character device */
		return 0;
	}
	errno = EBADF;
	return -1;
}

/* Implement some system calls to shut up the linker warnings */

#undef errno
extern int errno;

int __wrap__open(char *file, int flags, int mode)
{
	(void)file;
	(void)flags;
	(void)mode;
	errno = ENOSYS;
	return -1;
}

#else  /* if defined(STM32F4) */

#ifdef __GNUC__
#if ((__GNUC__ > 11) || \
     ((__GNUC__ == 11) && (__GNUC_MINOR__ >= 3)))
__attribute__((weak)) void _fstat() {}
__attribute__((weak)) void _isatty() {}
__attribute__((weak)) void _read() {}
__attribute__((weak)) void _write() {}
#endif
#endif

#endif	/* if defined(STM32F4) */

#ifdef __GNUC__
#if ((__GNUC__ > 11) || \
     ((__GNUC__ == 11) && (__GNUC_MINOR__ >= 3)))
__attribute__((weak)) void _close() {}
__attribute__((weak)) void _getpid() {}
__attribute__((weak)) void _kill() {}
__attribute__((weak)) void _lseek() {}
__attribute__((weak)) void _getentropy() {}
#endif
#endif


#endif	/* PLATFORM_ARM */

#ifdef __cplusplus
}
#endif
