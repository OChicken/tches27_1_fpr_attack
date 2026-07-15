#ifdef __cplusplus
extern "C" {
#endif

#include "stm32f4_hal.h"
#include "stm32f4xx_hal_conf.h"
#include <string.h>

UART_HandleTypeDef UartHandle;
RNG_HandleTypeDef RngHandle;

#ifdef STM32F415xx
uint8_t hw_key[16];
static CRYP_HandleTypeDef cryp;
#endif

/* from pqm4/common/test.c ***************************************************/

/* DWT macros are not put "globally" in hal.c b.c. NOT ALL platforms
   have these DWT registers. */
#define DWT_CTRL           (*(volatile uint32_t*)(0xE0001000u + 0x00))
#define DWT_CYCCNT         (*(volatile uint32_t*)(0xE0001000u + 0x04))
#define DWT_CTRL_CYCCNTENA (1 << 0)
#define SCS_DEMCR          (*(volatile uint32_t*)(0xE000E000u + 0xDFC))
#define SCS_DEMCR_TRCENA   (1 << 24)

void platform_init(void)
{
	//HAL_Init();

#ifdef STM32F4FPU
     /* set CP10 and CP11 Full Access */
     SCB->CPACR |= ((3UL << 10*2)|(3UL << 11*2)); // SCB->CPACR |= 0x00f00000;
#endif

#ifdef USE_INTERNAL_CLK
#pragma message "init by USE_INTERNAL_CLK settings"
     RCC_OscInitTypeDef RCC_OscInitStruct;
     RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
     RCC_OscInitStruct.HSEState       = RCC_HSE_OFF;
     RCC_OscInitStruct.HSIState       = RCC_HSI_ON;
	 RCC_OscInitStruct.PLL.PLLState   = RCC_PLL_ON;  // we need PLL to use RNG
	 RCC_OscInitStruct.PLL.PLLSource  = RCC_PLLSOURCE_HSI;
	 RCC_OscInitStruct.PLL.PLLM       = 16;  // Internal clock is 16MHz.
	 RCC_OscInitStruct.PLL.PLLN       = 336;
	 RCC_OscInitStruct.PLL.PLLP       = 2;
	 RCC_OscInitStruct.PLL.PLLQ       = 7;  // divisor for RNG, USB and SDIO
     HAL_RCC_OscConfig(&RCC_OscInitStruct);

     RCC_ClkInitTypeDef RCC_ClkInitStruct;
     RCC_ClkInitStruct.ClockType      = (RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2);
     RCC_ClkInitStruct.SYSCLKSource   = RCC_SYSCLKSOURCE_HSI;
     RCC_ClkInitStruct.AHBCLKDivider  = RCC_SYSCLK_DIV1;
     RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
     RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
     uint32_t flash_latency = 0;
     HAL_RCC_ClockConfig(&RCC_ClkInitStruct, flash_latency);
#elif USE_PLL
#pragma message "init by USE_PLL settings"
	RCC_OscInitTypeDef RCC_OscInitStruct;
	RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE | RCC_OSCILLATORTYPE_HSI;
	RCC_OscInitStruct.HSEState       = RCC_HSE_BYPASS;
	RCC_OscInitStruct.HSIState       = RCC_HSI_ON;  // HSI is needed for the RNG
	RCC_OscInitStruct.PLL.PLLState   = RCC_PLL_ON;  // we need PLL to use RNG
	RCC_OscInitStruct.PLL.PLLSource  = RCC_PLLSOURCE_HSE;
	RCC_OscInitStruct.PLL.PLLM       = 12;  // Internal clock is 16MHz
	RCC_OscInitStruct.PLL.PLLN       = 196;
	RCC_OscInitStruct.PLL.PLLP       = RCC_PLLP_DIV4;
	RCC_OscInitStruct.PLL.PLLQ       = 7;  // divisor for RNG, USB and SDIO
	if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK) {
        for(;;);
    }

	RCC_ClkInitTypeDef RCC_ClkInitStruct;
	RCC_ClkInitStruct.ClockType      = (RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2);
	RCC_ClkInitStruct.SYSCLKSource   = RCC_SYSCLKSOURCE_PLLCLK;
	RCC_ClkInitStruct.AHBCLKDivider  = RCC_SYSCLK_DIV1;
	RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
	RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;
	HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_ACR_LATENCY_5WS);
    FLASH->ACR |= 0b111 << 8; //enable ART acceleration
#elif USE_STM32F3
#pragma message "init by USE_STM32F3 settings"
	RCC_OscInitTypeDef RCC_OscInitStruct;
	RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE | RCC_OSCILLATORTYPE_HSI;
	RCC_OscInitStruct.HSEState       = RCC_HSE_BYPASS;
	RCC_OscInitStruct.HSIState       = RCC_HSI_OFF;
	RCC_OscInitStruct.PLL.PLLSource  = RCC_PLL_NONE;
	HAL_RCC_OscConfig(&RCC_OscInitStruct);

	RCC_ClkInitTypeDef RCC_ClkInitStruct;
	RCC_ClkInitStruct.ClockType      = (RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2);
	RCC_ClkInitStruct.SYSCLKSource   = RCC_SYSCLKSOURCE_HSE;
	RCC_ClkInitStruct.AHBCLKDivider  = RCC_SYSCLK_DIV1;
	RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
	RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
	uint32_t flash_latency = 0;
	HAL_RCC_ClockConfig(&RCC_ClkInitStruct, flash_latency);

#else
#pragma message "init by default settings, MCU FREQ = scope.clock.clkgen_freq"
	/* Clock path:
	 *   HSE (external) --> SYSCLK --> [AHB Divider] --> HCLK (CPU core clock)
	 *
	 * When BOTH of the following are set:
	 *   RCC_ClkInitStruct.SYSCLKSource   = RCC_SYSCLKSOURCE_HSE;  // SYSCLK = HSE
	 *   RCC_ClkInitStruct.AHBCLKDivider  = RCC_SYSCLK_DIV1;       // HCLK = SYSCLK / 1
	 *
	 * the following equality holds:
	 *   scope.clock.clkgen_freq = HSE = SYSCLK = HCLK = MCU core cycles per second
	 *
	 * This configuration is essential for side-channel analysis because it ensures
	 * the ADC sampling (derived from clkgen_freq) stays perfectly synchronized
	 * with the MCU's internal operations.
	 *
	 * Note: PLL is enabled separately for peripherals (RNG, USB, SDIO) but does
	 * not affect the CPU core clock:
	 *
	 *             +----------------------------------+
	 *             |              PLL                 |
	 *     HSE -+->| /PLLM -> *PLLN -> /PLLP, /PLLQ   |--> Peripherals (RNG, USB)
	 *          |  +----------------------------------+
	 *          |
	 *          +-> SYSCLK --> HCLK --> CPU core   <-- Your path (direct, no PLL)
	 *
	 * (Assumes scope.io.hs2 = "clkgen" and HS2 is connected to MCU clock input)
	 */

	/* ===== Oscillator Configuration ===== */
	RCC_OscInitTypeDef RCC_OscInitStruct;
	RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE | RCC_OSCILLATORTYPE_HSI;
	/* HSE (High Speed External): External clock from ChipWhisperer HS2 pin.
	 * RCC_HSE_BYPASS means we use an external clock signal, not a crystal. */
	RCC_OscInitStruct.HSEState       = RCC_HSE_BYPASS;
	RCC_OscInitStruct.HSIState       = RCC_HSI_ON;  // HSI is needed for the RNG
	/* PLL configuration (fed from HSE, but NOT used for CPU clock).
	 * PLL output = HSE / PLLM * PLLN / PLLP
	 * PLLQ output (for RNG/USB/SDIO) = HSE / PLLM * PLLN / PLLQ */
	RCC_OscInitStruct.PLL.PLLState   = RCC_PLL_ON;  // PLL ON for RNG peripheral
	RCC_OscInitStruct.PLL.PLLSource  = RCC_PLLSOURCE_HSE;
	RCC_OscInitStruct.PLL.PLLM       = 12;
	RCC_OscInitStruct.PLL.PLLN       = 196;
	RCC_OscInitStruct.PLL.PLLP       = RCC_PLLP_DIV4;
	RCC_OscInitStruct.PLL.PLLQ       = 7;  // divisor for RNG, USB and SDIO
	if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK) {
		for(;;);
	}

	/* ===== Clock Configuration ===== */
	RCC_ClkInitTypeDef RCC_ClkInitStruct;
	RCC_ClkInitStruct.ClockType      = (RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2);
	/* SYSCLKSource: Select HSE directly (NOT RCC_SYSCLKSOURCE_PLLCLK!)
	 * This is the key setting that makes MCU freq = scope.clock.clkgen_freq */
	RCC_ClkInitStruct.SYSCLKSource   = RCC_SYSCLKSOURCE_HSE;
	/* AHBCLKDivider = DIV1: No division, so HCLK = SYSCLK = HSE */
	RCC_ClkInitStruct.AHBCLKDivider  = RCC_SYSCLK_DIV1;
	RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
	RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
	HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_ACR_LATENCY_0WS); // 0 wait states OK for HSE
#endif

	// Configure and starts the RNG
	__HAL_RCC_RNG_CLK_ENABLE();
	RngHandle.Instance = RNG;
	RngHandle.State = HAL_RNG_STATE_RESET;
	HAL_RNG_Init(&RngHandle);

	/* Enable cycle counter */
	/* from /pqm4/common/test.c: cyccnt_enable() */
	SCS_DEMCR |= SCS_DEMCR_TRCENA;
	DWT_CYCCNT = 0;
	DWT_CTRL |= DWT_CTRL_CYCCNTENA;
}

void init_uart(void)
{
	GPIO_InitTypeDef GpioInit;
	GpioInit.Pin       = GPIO_PIN_9 | GPIO_PIN_10;
	GpioInit.Mode      = GPIO_MODE_AF_PP;
	GpioInit.Pull      = GPIO_PULLUP;
	GpioInit.Speed     = GPIO_SPEED_FREQ_HIGH;
	GpioInit.Alternate = GPIO_AF7_USART1;
	__GPIOA_CLK_ENABLE();
	HAL_GPIO_Init(GPIOA, &GpioInit);

	UartHandle.Instance        = USART1;
  #if SS_VER==SS_VER_2_1
	#pragma message "Using 230400 baud rate for SS_VER_2_1"
  UartHandle.Init.BaudRate   = 230400;
  #elif SS_VER==SS_VER_1_1 || SS_VER==SS_VER_1_0
  	#pragma message "Using 38400 baud rate for SS_VER_1_1"
  UartHandle.Init.BaudRate   = 38400;
  #else
  	#pragma error ("SS_VERnot defined or unsupported version! Close.")
  #endif
	UartHandle.Init.WordLength = UART_WORDLENGTH_8B;
	UartHandle.Init.StopBits   = UART_STOPBITS_1;
	UartHandle.Init.Parity     = UART_PARITY_NONE;
	UartHandle.Init.HwFlowCtl  = UART_HWCONTROL_NONE;
	UartHandle.Init.Mode       = UART_MODE_TX_RX;
	__USART1_CLK_ENABLE();
	HAL_UART_Init(&UartHandle);
}

//#define STM32F4_WLCSP

void trigger_setup(void)
{
	__GPIOA_CLK_ENABLE();
#ifdef STM32F4_WLCSP
 	GPIO_InitTypeDef GpioInit;
	GpioInit.Pin       = GPIO_PIN_4;
	GpioInit.Mode      = GPIO_MODE_OUTPUT_PP;
	GpioInit.Pull      = GPIO_NOPULL;
	GpioInit.Speed     = GPIO_SPEED_FREQ_HIGH;
    __GPIOD_CLK_ENABLE();
    HAL_GPIO_Init(GPIOD, &GpioInit);
#else
	GPIO_InitTypeDef GpioInit;
	GpioInit.Pin       = GPIO_PIN_12;
	GpioInit.Mode      = GPIO_MODE_OUTPUT_PP;
	GpioInit.Pull      = GPIO_NOPULL;
	GpioInit.Speed     = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOA, &GpioInit);
#endif
	HAL_GPIO_WritePin(GPIOA, GPIO_PIN_12, GPIO_PIN_RESET);
}

void trigger_high(void)
{
#ifdef STM32F4_WLCSP
    HAL_GPIO_WritePin(GPIOD, GPIO_PIN_4, GPIO_PIN_SET);
#else
	HAL_GPIO_WritePin(GPIOA, GPIO_PIN_12, GPIO_PIN_SET);
#endif
}

void trigger_low(void)
{
#ifdef STM32F4_WLCSP
    HAL_GPIO_WritePin(GPIOD, GPIO_PIN_4, GPIO_PIN_RESET);
#else
	HAL_GPIO_WritePin(GPIOA, GPIO_PIN_12, GPIO_PIN_RESET);
#endif
}

char getch(void)
{
	uint8_t d;
	while (HAL_UART_Receive(&UartHandle, &d, 1, 5000) != HAL_OK);
	return d;
}

void putch(char c)
{
	uint8_t d  = c;
	HAL_UART_Transmit(&UartHandle,  &d, 1, 5000);
}

static int rng_recover(void) {
    __HAL_RCC_RNG_FORCE_RESET();
    __HAL_RCC_RNG_RELEASE_RESET();
    return (HAL_RNG_Init(&RngHandle) == HAL_OK) ? 0 : -1;
}

/* Fill `out` with `outlen` random bytes from the STM32 RNG peripheral.
   Returns 0 on success, -1 on failure. */
int _randombytes(uint8_t *out, size_t outlen)
{
	while (outlen > 0) {
		uint32_t w;
		HAL_StatusTypeDef st;
		/* Busy can happen if RNG is in use elsewhere / just wait and retry. */
		do {
			st = HAL_RNG_GenerateRandomNumber(&RngHandle, &w);
		} while (st == HAL_BUSY);

		if (st != HAL_OK) {
			/* Try one recovery re-init; if that fails, bail out. */
			if (rng_recover() < 0)
				return -1;
			/* Try once more after recovery */
			st = HAL_RNG_GenerateRandomNumber(&RngHandle, &w);
			if (st != HAL_OK)
				return -1;
		}

		size_t n = (outlen < 4) ? outlen : 4;
		/* Endianness doesn’t matter for randomness; memcpy is fine. */
		memcpy(out, &w, n);
		out     += n;
		outlen  -= n;
	}
	return 0;
}

uint32_t get_rand(void)
{
	uint32_t prev_rand = RngHandle.RandomNumber;
	uint32_t next_rand;
	HAL_StatusTypeDef error;

	do {
		error = HAL_RNG_GenerateRandomNumber(&RngHandle, &next_rand);
  	} while (error != HAL_OK && prev_rand == next_rand);
  	return next_rand;
}

#ifdef STM32F415xx

void HW_AES128_Init(void)
{
	cryp.Instance = CRYP;
	cryp.Init.DataType = CRYP_DATATYPE_8B;
	cryp.Init.KeySize = CRYP_KEYSIZE_128B;
	cryp.Init.pKey = hw_key;
  HW_AES128_LoadKey(hw_key);
  __HAL_RCC_CRYP_CLK_ENABLE();
	HAL_CRYP_Init(&cryp);
}

void HW_AES128_LoadKey(uint8_t* key)
{
	for(int i = 0; i < 16; i++)
	{
		cryp.Init.pKey[i] = key[i];
	}
}

void HW_AES128_Enc_pretrigger(uint8_t* pt)
{
    HAL_CRYP_Init(&cryp);
}

void HW_AES128_Enc(uint8_t* pt)
{
    HAL_CRYP_AESECB_Encrypt(&cryp, pt, 16, pt, 1000);
}

void HW_AES128_Enc_posttrigger(uint8_t* pt)
{
    ;
}

void HW_AES128_Dec(uint8_t *pt)
{
     HAL_CRYP_Init(&cryp);
     HAL_CRYP_AESECB_Decrypt(&cryp, pt, 16, pt, 1000);
}

#endif

#ifdef __cplusplus
}
#endif
