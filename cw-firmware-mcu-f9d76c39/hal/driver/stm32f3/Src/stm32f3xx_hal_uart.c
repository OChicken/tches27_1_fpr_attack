#include "stm32f3xx_hal.h"

#define UART_CR1_FIELDS  ((uint32_t)(USART_CR1_M | USART_CR1_PCE | USART_CR1_PS | \
                                     USART_CR1_TE | USART_CR1_RE | USART_CR1_OVER8)) /*!< UART or USART CR1 fields of parameters set by UART_SetConfig API */

/**
  * @brief Configure the UART peripheral.
  * @param huart: UART handle.
  * @retval HAL status
  */
HAL_StatusTypeDef UART_SetConfig(UART_HandleTypeDef *huart)
{
  uint32_t tmpreg                     = 0x00000000U;
  UART_ClockSourceTypeDef clocksource = UART_CLOCKSOURCE_UNDEFINED;
  uint16_t brrtemp                    = 0x0000U;
  uint16_t usartdiv                   = 0x0000U;
  HAL_StatusTypeDef ret               = HAL_OK;

  /* Check the parameters */
  assert_param(IS_UART_BAUDRATE(huart->Init.BaudRate));
  assert_param(IS_UART_WORD_LENGTH(huart->Init.WordLength));
  assert_param(IS_UART_STOPBITS(huart->Init.StopBits));
  assert_param(IS_UART_PARITY(huart->Init.Parity));
  assert_param(IS_UART_MODE(huart->Init.Mode));
  assert_param(IS_UART_HARDWARE_FLOW_CONTROL(huart->Init.HwFlowCtl));
  assert_param(IS_UART_ONE_BIT_SAMPLE(huart->Init.OneBitSampling));
  assert_param(IS_UART_OVERSAMPLING(huart->Init.OverSampling));


  /*-------------------------- USART CR1 Configuration -----------------------*/
  /* Clear M, PCE, PS, TE, RE and OVER8 bits and configure
   *  the UART Word Length, Parity, Mode and oversampling:
   *  set the M bits according to huart->Init.WordLength value
   *  set PCE and PS bits according to huart->Init.Parity value
   *  set TE and RE bits according to huart->Init.Mode value
   *  set OVER8 bit according to huart->Init.OverSampling value */
  tmpreg = (uint32_t)huart->Init.WordLength | huart->Init.Parity | huart->Init.Mode | huart->Init.OverSampling ;
  MODIFY_REG(huart->Instance->CR1, UART_CR1_FIELDS, tmpreg);

  /*-------------------------- USART CR2 Configuration -----------------------*/
  /* Configure the UART Stop Bits: Set STOP[13:12] bits according
   * to huart->Init.StopBits value */
  MODIFY_REG(huart->Instance->CR2, USART_CR2_STOP, huart->Init.StopBits);

  /*-------------------------- USART CR3 Configuration -----------------------*/
  /* Configure
   * - UART HardWare Flow Control: set CTSE and RTSE bits according
   *   to huart->Init.HwFlowCtl value
   * - one-bit sampling method versus three samples' majority rule according
   *   to huart->Init.OneBitSampling */
  tmpreg = (uint32_t)huart->Init.HwFlowCtl | huart->Init.OneBitSampling ;
  MODIFY_REG(huart->Instance->CR3, (USART_CR3_RTSE | USART_CR3_CTSE | USART_CR3_ONEBIT), tmpreg);

  /*-------------------------- USART BRR Configuration -----------------------*/
  UART_GETCLOCKSOURCE(huart, clocksource);

  /* Check UART Over Sampling to set Baud Rate Register */
  if (huart->Init.OverSampling == UART_OVERSAMPLING_8)
  {
    switch (clocksource)
    {
      case UART_CLOCKSOURCE_PCLK1:
        usartdiv = (uint16_t)(UART_DIV_SAMPLING8(HAL_RCC_GetPCLK1Freq(), huart->Init.BaudRate));
        break;
      case UART_CLOCKSOURCE_PCLK2:
        usartdiv = (uint16_t)(UART_DIV_SAMPLING8(HAL_RCC_GetPCLK2Freq(), huart->Init.BaudRate));
        break;
      case UART_CLOCKSOURCE_HSI:
        usartdiv = (uint16_t)(UART_DIV_SAMPLING8(HSI_VALUE, huart->Init.BaudRate));
        break;
      case UART_CLOCKSOURCE_SYSCLK:
        usartdiv = (uint16_t)(UART_DIV_SAMPLING8(HAL_RCC_GetSysClockFreq(), huart->Init.BaudRate));
        break;
      case UART_CLOCKSOURCE_LSE:
        usartdiv = (uint16_t)(UART_DIV_SAMPLING8(LSE_VALUE, huart->Init.BaudRate));
        break;
      case UART_CLOCKSOURCE_UNDEFINED:
      default:
        ret = HAL_ERROR;
        break;
    }

    brrtemp = usartdiv & 0xFFF0U;
    brrtemp |= (uint16_t)((usartdiv & (uint16_t)0x000FU) >> 1U);
    huart->Instance->BRR = brrtemp;
  }
  else
  {
    switch (clocksource)
    {
      case UART_CLOCKSOURCE_PCLK1:
        huart->Instance->BRR = (uint16_t)(UART_DIV_SAMPLING16(HAL_RCC_GetPCLK1Freq(), huart->Init.BaudRate));
        break;
      case UART_CLOCKSOURCE_PCLK2:
        huart->Instance->BRR = (uint16_t)(UART_DIV_SAMPLING16(HAL_RCC_GetPCLK2Freq(), huart->Init.BaudRate));
        break;
      case UART_CLOCKSOURCE_HSI:
        huart->Instance->BRR = (uint16_t)(UART_DIV_SAMPLING16(HSI_VALUE, huart->Init.BaudRate));
        break;
      case UART_CLOCKSOURCE_SYSCLK:
        huart->Instance->BRR = (uint16_t)(UART_DIV_SAMPLING16(HAL_RCC_GetSysClockFreq(), huart->Init.BaudRate));
        break;
      case UART_CLOCKSOURCE_LSE:
        huart->Instance->BRR = (uint16_t)(UART_DIV_SAMPLING16(LSE_VALUE, huart->Init.BaudRate));
        break;
      case UART_CLOCKSOURCE_UNDEFINED:
      default:
        ret = HAL_ERROR;
        break;
    }
  }

  return ret;

}

/**
  * @brief Check the UART Idle State.
  * @param huart UART handle.
  * @retval HAL status
  */
HAL_StatusTypeDef UART_CheckIdleState(UART_HandleTypeDef *huart)
{
  uint32_t tickstart = 0U;

  /* Initialize the UART ErrorCode */
  huart->ErrorCode = HAL_UART_ERROR_NONE;

  /* Init tickstart for timeout managment*/
  tickstart = HAL_GetTick();

  /* Check if the Transmitter is enabled */
  if((huart->Instance->CR1 & USART_CR1_TE) == USART_CR1_TE)
  {
    /* Wait until TEACK flag is set */
    if(UART_WaitOnFlagUntilTimeout(huart, USART_ISR_TEACK, RESET, tickstart, HAL_UART_TIMEOUT_VALUE) != HAL_OK)
    {
      /* Timeout Occured */
      return HAL_TIMEOUT;
    }
  }
  /* Check if the Receiver is enabled */
  if((huart->Instance->CR1 & USART_CR1_RE) == USART_CR1_RE)
  {
    /* Wait until REACK flag is set */
    if(UART_WaitOnFlagUntilTimeout(huart, USART_ISR_REACK, RESET, tickstart, HAL_UART_TIMEOUT_VALUE) != HAL_OK)
    {
      /* Timeout Occured */
      return HAL_TIMEOUT;
    }
  }

  /* Initialize the UART State */
  huart->gState  = HAL_UART_STATE_READY;
  huart->RxState = HAL_UART_STATE_READY;

  /* Process Unlocked */
  __HAL_UNLOCK(huart);

  return HAL_OK;
}

/**
  * @brief Initialize the UART mode according to the specified
  *        parameters in the UART_InitTypeDef and initialize the associated handle.
  * @param huart: UART handle.
  * @retval HAL status
  */
HAL_StatusTypeDef HAL_UART_Init(UART_HandleTypeDef *huart)
{
  /* Check the UART handle allocation */
  if(huart == NULL)
  {
    return HAL_ERROR;
  }

  if(huart->Init.HwFlowCtl != UART_HWCONTROL_NONE)
  {
    /* Check the parameters */
    assert_param(IS_UART_HWFLOW_INSTANCE(huart->Instance));
  }
  else
  {
    /* Check the parameters */
    assert_param(IS_UART_INSTANCE(huart->Instance));
  }

  if(huart->gState == HAL_UART_STATE_RESET)
  {
    /* Allocate lock resource and initialize it */
    huart->Lock = HAL_UNLOCKED;

    /* Init the low level hardware : GPIO, CLOCK */
    //HAL_UART_MspInit(huart);
  }

  huart->gState = HAL_UART_STATE_BUSY;

  /* Disable the Peripheral */
  __HAL_UART_DISABLE(huart);

  /* Set the UART Communication parameters */
  if (UART_SetConfig(huart) == HAL_ERROR)
  {
    return HAL_ERROR;
  }

  if (huart->AdvancedInit.AdvFeatureInit != UART_ADVFEATURE_NO_INIT)
  {
    //UART_AdvFeatureConfig(huart);
  }

  /* In asynchronous mode, the following bits must be kept cleared:
  - LINEN and CLKEN bits in the USART_CR2 register,
  - SCEN, HDSEL and IREN  bits in the USART_CR3 register.*/
  CLEAR_BIT(huart->Instance->CR2, (USART_CR2_LINEN | USART_CR2_CLKEN));
  CLEAR_BIT(huart->Instance->CR3, (USART_CR3_SCEN | USART_CR3_HDSEL | USART_CR3_IREN));

  /* Enable the Peripheral */
  __HAL_UART_ENABLE(huart);

  /* TEACK and/or REACK to check before moving huart->gState and huart->RxState to Ready */
  return UART_CheckIdleState(huart);
}

/**
  * @brief  Handle UART Communication Timeout.
  * @param  huart UART handle.
  * @param  Flag Specifies the UART flag to check
  * @param  Status Flag status (SET or RESET)
  * @param  Tickstart Tick start value
  * @param  Timeout Timeout duration
  * @retval HAL status
  */
HAL_StatusTypeDef UART_WaitOnFlagUntilTimeout(UART_HandleTypeDef *huart, uint32_t Flag, FlagStatus Status, uint32_t Tickstart, uint32_t Timeout)
{
  /* Wait until flag is set */
  while((__HAL_UART_GET_FLAG(huart, Flag) ? SET : RESET) == Status)
  {
    /* Check for the Timeout */
    if(Timeout != HAL_MAX_DELAY)
    {
      if((Timeout == 0U) || ((HAL_GetTick()-Tickstart) > Timeout))
      {
        /* Disable TXE, RXNE, PE and ERR (Frame error, noise error, overrun error) interrupts for the interrupt process */
        CLEAR_BIT(huart->Instance->CR1, (USART_CR1_RXNEIE | USART_CR1_PEIE | USART_CR1_TXEIE));
        CLEAR_BIT(huart->Instance->CR3, USART_CR3_EIE);

        huart->gState  = HAL_UART_STATE_READY;
        huart->RxState = HAL_UART_STATE_READY;

        /* Process Unlocked */
        __HAL_UNLOCK(huart);
        return HAL_TIMEOUT;
      }
    }
  }
  return HAL_OK;
}

/**
  * @brief Send an amount of data in blocking mode.
  * @param huart: UART handle.
  * @param pData: Pointer to data buffer.
  * @param Size: Amount of data to be sent.
  * @param Timeout: Timeout duration.
  * @retval HAL status
  */
HAL_StatusTypeDef HAL_UART_Transmit(UART_HandleTypeDef *huart, uint8_t *pData, uint16_t Size, uint32_t Timeout)
{
  uint16_t* tmp;
  uint32_t tickstart = 0U;

  /* Check that a Tx process is not already ongoing */
  if(huart->gState == HAL_UART_STATE_READY)
  {
    if((pData == NULL ) || (Size == 0U))
    {
      return  HAL_ERROR;
    }

    /* Process Locked */
    __HAL_LOCK(huart);

    huart->ErrorCode = HAL_UART_ERROR_NONE;
    huart->gState = HAL_UART_STATE_BUSY_TX;

    /* Init tickstart for timeout managment*/
    tickstart = HAL_GetTick();

    huart->TxXferSize = Size;
    huart->TxXferCount = Size;
    while(huart->TxXferCount > 0U)
    {
      huart->TxXferCount--;
      if(UART_WaitOnFlagUntilTimeout(huart, UART_FLAG_TXE, RESET, tickstart, Timeout) != HAL_OK)
      {
        return HAL_TIMEOUT;
      }
      if ((huart->Init.WordLength == UART_WORDLENGTH_9B) && (huart->Init.Parity == UART_PARITY_NONE))
      {
        tmp = (uint16_t*) pData;
        huart->Instance->TDR = (*tmp & (uint16_t)0x01FFU);
        pData += 2U;
      }
      else
      {
        huart->Instance->TDR = (*pData++ & (uint8_t)0xFFU);
      }
    }
    if(UART_WaitOnFlagUntilTimeout(huart, UART_FLAG_TC, RESET, tickstart, Timeout) != HAL_OK)
    {
      return HAL_TIMEOUT;
    }

    /* At end of Tx process, restore huart->gState to Ready */
    huart->gState = HAL_UART_STATE_READY;

    /* Process Unlocked */
    __HAL_UNLOCK(huart);

    return HAL_OK;
  }
  else
  {
    return HAL_BUSY;
  }
}

/**
  * @brief Receive an amount of data in blocking mode.
  * @param huart: UART handle.
  * @param pData: pointer to data buffer.
  * @param Size: amount of data to be received.
  * @param Timeout: Timeout duration.
  * @retval HAL status
  */
HAL_StatusTypeDef HAL_UART_Receive(UART_HandleTypeDef *huart, uint8_t *pData, uint16_t Size, uint32_t Timeout)
{
  uint16_t* tmp;
  uint16_t uhMask;
  uint32_t tickstart = 0U;

  /* Check that a Rx process is not already ongoing */
  if(huart->RxState == HAL_UART_STATE_READY)
  {
    if((pData == NULL ) || (Size == 0U))
    {
      return  HAL_ERROR;
    }

    /* Process Locked */
    __HAL_LOCK(huart);

    huart->Instance->ICR = 0xFFFFFFFF;
    huart->ErrorCode = HAL_UART_ERROR_NONE;
    huart->RxState = HAL_UART_STATE_BUSY_RX;

    /* Init tickstart for timeout managment*/
    tickstart = HAL_GetTick();

    huart->RxXferSize = Size;
    huart->RxXferCount = Size;

    /* Computation of UART mask to apply to RDR register */
    UART_MASK_COMPUTATION(huart);
    uhMask = huart->Mask;

    /* as long as data have to be received */
    while(huart->RxXferCount > 0U)
    {
      huart->RxXferCount--;
      if(UART_WaitOnFlagUntilTimeout(huart, UART_FLAG_RXNE, RESET, tickstart, Timeout) != HAL_OK)
      {
        return HAL_TIMEOUT;
      }
      if ((huart->Init.WordLength == UART_WORDLENGTH_9B) && (huart->Init.Parity == UART_PARITY_NONE))
      {
        tmp = (uint16_t*) pData ;
        *tmp = (uint16_t)(huart->Instance->RDR & uhMask);
        pData +=2U;
      }
      else
      {
        *pData++ = (uint8_t)(huart->Instance->RDR & (uint8_t)uhMask);
      }
    }

    /* At end of Rx process, restore huart->RxState to Ready */
    huart->RxState = HAL_UART_STATE_READY;

    /* Process Unlocked */
    __HAL_UNLOCK(huart);

    return HAL_OK;
  }
  else
  {
    return HAL_BUSY;
  }
}
