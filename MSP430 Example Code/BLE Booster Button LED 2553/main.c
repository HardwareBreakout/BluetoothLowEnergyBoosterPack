/******************************************************************************
 *                  Value Line LaunchPad BLE Booster Demo
 *
 * Description: This is the code used to demo the BLE Booster board sold at
 * 				the Hardware Breakout store. The BLE Booster Board is
 * 				compatible with the Value Line LaunchPad and the MSP4305229
 * 				LaunchPad. This is the demo code for the Value Line LaunchPad.
 *
 * 				When paired with the Python application or Android
 * 				application, the following features are available:
 * 					- The on board LED can be toggled
 * 					- Button presses can be counted
 * 					- Informative text can be sent
 * 					- VCC can be measured
 * 					- Internal temperature can be measured
 * 					- Battery voltage can be measured
 *
 *              This code was originally created for the "Hardware
 *              Breakout Store".
 *
 *              http://store.hardwarebreakout.com
 *
 * Author:  Nicholas J. Conn - http://msp430launchpad.com
 * Email:   webmaster at msp430launchpad.com
 * Date:    12-20-13
 ******************************************************************************/

#include  <msp430g2553.h>
#include "stdarg.h"

// Flag for StatusRegister which allows interrupts to communicate with the main loop
#define UART_RX			BIT0
#define BUTTON			BIT1
#define ADC				BIT2

// Character commands from the computer
#define LED_TOGGLE		0x31	// "1"
#define HELLO_WORLD		0x32	// "2"
#define AUTHOR_INFO		0x33	// "3"
#define GET_VCC			0x34	// "4"
#define GET_TEMP		0x35	// "5"
#define GET_BATTERY		0x36	// "6"


unsigned char StatusRegister;
unsigned char UART_RXData;					// Byte received via UART
unsigned int ADCValue;						// Value measured from ADC

// Function declarations
void printf(char *, ...);
void Initialize(void);
void SendByte_UART(unsigned char);
void measureVCC(void);
void measureTemp(void);
void measureBattery(void);


void main(void)
{
	WDTCTL = WDTPW + WDTHOLD;                 // Stop WDT
	BCSCTL1 = CALBC1_1MHZ;                    // Set calibrated DCO values
	DCOCTL = CALDCO_1MHZ;

	// Initialize UART and I/O
	Initialize();

	// Main running loop
	while (1)
	{
		// Determine which flags are set and run code accordingly
		switch(StatusRegister)
		{
			// No flag set
			case 0:
				__bis_SR_register(LPM0_bits + GIE);		// Enter LPM0, interrupts enabled
				break;

			// UART byte received
			case UART_RX:
				StatusRegister &= ~UART_RX;				// Clears the Status Flag

				// Determine which command was sent
				switch (UART_RXData)
				{
					case LED_TOGGLE:
						P1OUT ^= BIT0;
						break;

					case HELLO_WORLD:
						printf("Hello World!\n");
						break;

					case AUTHOR_INFO:
						printf("NJC from http://store.hardwarebreakout.com!\n");
						break;

					case GET_VCC:
						measureVCC();
						break;

					case GET_TEMP:
						measureTemp();
						break;

					case GET_BATTERY:
						measureBattery();
						break;

					default: break;
				}
				break;

			// Button pressed
			case BUTTON:
				StatusRegister &= ~BUTTON;			// Clears the Status Flag
				SendByte_UART('b');						// Sent 'b' representing button press
				break;

			// ADC Value received
			case ADC:
				StatusRegister &= ~ADC;			// Clears the Status Flag
				ADCValue = ADCValue >> 2;		// Shifts the 10-bit value down to 8 bits
				SendByte_UART(ADCValue);		// Send ADC byte
				break;

		}
	}
}

/**
* Initialize all pins and UART. Note: ADC is not initialized here
**/
void Initialize(void)
{
	P1DIR = BIT0;
	P1OUT &= ~BIT0 + BIT6;

	// Button interrupt pin initialization
	P1DIR &= ~BIT3;							// Set P1.3 to input direction
	P1IE |= BIT3;							// P1.3 interrupt enabled
	P1IES |= BIT3;							// Interrupt on P1.3 Hi/lo edge
	P1IFG &= ~BIT3;							// P1.3 IFG cleared

	// Initialize UART
	P1SEL = BIT1 + BIT2;					// Set P1.1 = RXD, P1.2=TXD
	P1SEL2 = BIT1 + BIT2;
	UCA0CTL1 |= UCSSEL_2;					// SMCLK and base clock
	UCA0BR0 = 104;                          // 1MHz/104 9600
	UCA0BR1 = 0;							// 1MHz 9600
	UCA0MCTL = UCBRS2 + UCBRS0;				// Modulation UCBRSx = 5
	UCA0CTL1 &= ~UCSWRST;					// **Initialize USCI state machine**
	IE2 |= UCA0RXIE;						// Enable USCI_A0 RX interrupt
}

/**
* Start a VCC measurement using the internal reference. An ADC interrupt will be thrown.
*	This simply initialized the ADC for a single measurement. NOTE: This can measure a
*	maximum of 3V VCC since 1.5V ref is used. If you would like to measure higher, use a
*	2.5V reference.
**/
void measureVCC(void)
{
	ADC10CTL0 &= ~ENC;									// Disable ADC
	// Use reference, 16 clock ticks, internal 1.5V reference on, interrupt enable
	// NOTE: This can measure a maximum of 3V VCC since 1.5V ref is used
	ADC10CTL0 = SREF_1 + ADC10SHT_3 + REFON + ADC10ON + ADC10IE;
	ADC10CTL1 = ADC10DIV_3 + ADC10SSEL_3 + INCH_11;		// divider /4, set VCC channel, SMCLK
	__delay_cycles (128);								// Delay to allow Ref to settle
	ADC10CTL0 |= ENC + ADC10SC;							// Start single measurement
}

/**
* Start a temperature measurement using the internal temperature sensor and 1.5V
* 	reference.
**/
void measureTemp(void)
{
	ADC10CTL0 &= ~ENC;									// Disable ADC
	ADC10CTL1 = ADC10DIV_3 + INCH_10;					// divider /8, set temperature channel, SMCLK
	// Use reference, 16 clock ticks, internal 1.5V reference on, interrupt enable
	ADC10CTL0 = SREF_1 + ADC10SHT_3 + REFON + ADC10ON + ADC10IE;
	__delay_cycles (128);								// Delay to allow Ref to settle
	ADC10CTL0 |= ENC + ADC10SC;							// Start single measurement
}

/**
* Start an external measurement to measure the battery voltage using A6.
* 	NOTE: This uses VCC as a reference voltage, you should measure VCC
* 	first to ensure accurate measurement of the battery voltage.
**/
void measureBattery(void)
{
//	// Enable FET for measurement
//	P1IE &= ~BIT3;								// P1.3 interrupt disabled
//	P1DIR |= BIT3;								// Set P1.3 to output direction
//	P1OUT &= ~BIT3;								// Set P1.3 low

	ADC10CTL0 &= ~ENC;									// Disable ADC
	// 16 clock ticks, interrupt enable
	ADC10CTL0 = ADC10SHT_3 + ADC10ON + ADC10IE;			// Sample and hold time, adc on, interrupt enable
	ADC10CTL1 = ADC10DIV_3 + ADC10SSEL_3 + INCH_4;		// divider /4, set VCC channel, SMCLK
	__delay_cycles (128);								// Delay to allow Ref to settle
	ADC10CTL0 |= ENC + ADC10SC;							// Start single measurement
}

/**
 * puts() is used by printf() to display or send a string.. This function
 *     determines where printf prints to. For this case it sends a string
 *     out over UART, another option could be to display the string on an
 *     LCD display.
 **/
void puts(char *s) {
	char c;

	// Loops through each character in string 's'
	while (c = *s++) {
		SendByte_UART(c);
	}
}

/**
 * puts() is used by printf() to display or send a character. This function
 *     determines where printf prints to. For this case it sends a character
 *     out over UART.
 **/
void putc(unsigned b) {
	SendByte_UART(b);
}

/**
* Send a 8 bit char using the UART
**/
void SendByte_UART(unsigned char txValue)
{
	while (!(IFG2&UCA0TXIFG));					// USCI_A0 TX buffer ready?
//	while ( (FLOW_PIN & RTS) );
	UCA0TXBUF = txValue;						// Send 8-bit character
}

/**
* UART receive interrupt.
**/
#pragma vector=USCIAB0RX_VECTOR
__interrupt void USCI0RX_ISR(void)
{
	UART_RXData = UCA0RXBUF;				// Received byte to UART_RXData
	StatusRegister |= UART_RX;				// Set the UART_RX flag for the main loop
	__bic_SR_register_on_exit(LPM0_bits);	// Wake-up CPU
}

/**
* Button press P1.3 interrupt
**/
#pragma vector=PORT1_VECTOR
__interrupt void Port_1(void)
{
	// Toggle LED when button pressed (for visual indication)
	P1OUT ^= BIT0;
	P1IFG &= ~BIT3;							// P1.3 IFG cleared loop for button press

	StatusRegister |= BUTTON;				// Set the BUTTON flag for the main loop
	__bic_SR_register_on_exit(LPM0_bits);	// Wake-up CPU
}

/**
* ADC12 Interrupt.
**/
#pragma vector=ADC10_VECTOR
__interrupt void ADC10_ISR (void)
{
	ADCValue = ADC10MEM;					// Saves measured value.

	// Re-enable the button interrupt (might be disabled for battery measurement).
	P1DIR &= ~BIT3;							// Set P1.3 to input direction
	P1IE |= BIT3;							// P1.3 interrupt enabled
	P1IES |= BIT3;							// P1.3 Hi/lo edge
	P1IFG &= ~BIT3;							// P1.3 IFG cleared

	StatusRegister |= ADC;					// Set ADC flag
	__bic_SR_register_on_exit(LPM0_bits);	// Wake-up CPU
}
