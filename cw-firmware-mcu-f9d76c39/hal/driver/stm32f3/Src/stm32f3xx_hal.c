#include "stm32f3xx_hal.h"

uint32_t hal_sys_tick = 0;
__IO uint32_t uwTick = 0;

#ifndef ENABLE_TICK_TIMING
HAL_StatusTypeDef HAL_InitTick(uint32_t TickPriority)
{
	hal_sys_tick = 0;
	return HAL_OK;
}
uint32_t HAL_GetTick(void)
{
	return hal_sys_tick++;
}
void HAL_IncTick(void)
{
}
#else
__weak HAL_StatusTypeDef HAL_InitTick(uint32_t TickPriority)
{
  /*Configure the SysTick to have interrupt in 1ms time basis*/
  HAL_SYSTICK_Config(SystemCoreClock / 1000U);

  /*Configure the SysTick IRQ priority */
  HAL_NVIC_SetPriority(SysTick_IRQn, TickPriority ,0U);

   /* Return function status */
  return HAL_OK;
}
__weak uint32_t HAL_GetTick(void)
{
  return uwTick;
}

__weak void HAL_IncTick(void)
{
  uwTick++;
}
#endif
