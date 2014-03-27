/******************************************************************************
 *                  MSP430F5529 LaunchPad BLE Booster Demo
 *
 * Description: This is the code used to demo the BLE Booster board sold at
 * 				the Hardware Breakout store. The BLE Booster Board is
 * 				compatible with the Value Line LaunchPad and the MSP4305229
 * 				LaunchPad. This is the demo code for the 5529 LaunchPad.
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

#include  <msp430f5529.h>
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
	WDTCTL = WDTPW + WDTHOLD;				// Stop WDT
	REFCTL0 &= ~REFMSTR;					// Reset REFMSTR to hand over control to
												// ADC12_A ref control registers
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
				StatusRegister &= ~BUTTON;				// Clears the Status Flag
				SendByte_UART('b');						// Sent 'b' representing button press
				break;

			// ADC Value received
			case ADC:
				StatusRegister &= ~ADC;					// Clears the Status Flag
				//ADCValue = ADCValue >> 2;				// No shift needed, ADC in 8 bit mode
				SendByte_UART(ADCValue);				// Send ADC byte
				break;

		}
	}
}

/**
* Initialize all pins and UART. Note: ADC is not initialized here
**/
void Initialize(void)
{
	// Initialize LED pin
	P1DIR = BIT0;
	P1OUT &= ~BIT0;

	P6SEL |= BIT6;							// Set P6.6 to ADC input

	// Button interrupt pin initialization
	P2DIR &= ~BIT1;							// Set P2.1 to input direction
	P2REN |= BIT1;							// Enable P2.1 internal resistance
	P2OUT |= BIT1;							// Set P2.1 as pull-Up resistance
	P2IES |= BIT1;							// Interrupt on P2.1 Hi/lo edge
	P2IFG &= ~BIT1;							// P2.1 IFG cleared
	P2IE |= BIT1;							// P2.1 interrupt enabled

	// Initialize UART
	P3SEL |= BIT3+BIT4;						// P3.3,4 = USCI_A0 TXD/RXD
	UCA0CTL1 |= UCSWRST;					// **Put state machine in reset**
	UCA0CTL1 |= UCSSEL_2;					// SMCLK
	UCA0BR0 = 104;							// 1MHz/104 = 9600
	UCA0BR1 = 0;							// 1MHz 9600
	UCA0MCTL = UCBRS2 + UCBRS0;				// Modulation UCBRSx = 5
	UCA0CTL1 &= ~UCSWRST;					// **Initialize USCI state machine**
	UCA0IE |= UCRXIE;       				// Enable USCI_A0 RX interrupt
}

/**
* Start a VCC measurement using the internal reference. An ADC interrupt will be thrown.
*	This simply initialized the ADC for a single measurement. NOTE: This can measure a
*	maximum of 3V VCC since 1.5V ref is used. If you would like to measure higher, use a
*	2.5V reference.
**/
void measureVCC(void)
{
	ADC12CTL0 &= ~ADC12ENC;								// Disable ADC

	// Use reference, 16 clock ticks, internal 1.5V reference on
	ADC12CTL0 = ADC12SHT0_3 + ADC12REFON + ADC12ON;
	ADC12CTL1 = ADC12SHP + ADC12DIV_7 + ADC12SSEL_3;	// divider /8, SMCLK
	// 8-bit, enable reference out, workaround for bad Vreference (device errata)
	ADC12CTL2 = ADC12RES_0 + ADC12REFOUT;
	// Set interrupt location 1 (ADCMEMO) to use reference and VCC input
	ADC12MCTL0 = ADC12SREF1 + ADC12INCH_11;
	ADC12IE = 0x001;									// Enable interrupt for ADCMEMO
	__delay_cycles (128);								// Delay to allow Ref to settle
	ADC12CTL0 |= ADC12ENC;								// Start single measurement
    ADC12CTL0 |= ADC12SC;                   			// Sampling and conversion start
}

/**
* Start a temperature measurement using the internal temperature sensor and 1.5V
* 	reference. NOTE: The MSP430F5529 calibration data is not accurate (device errata).
* 	You must calibrate the device manually if you wish for accurate measurements.
**/
void measureTemp(void)
{
	ADC12CTL0 &= ~ADC12ENC;								// Disable ADC

	// Use reference, 16 clock ticks, internal 1.5V reference on
	ADC12CTL0 = ADC12SHT0_3 + ADC12REFON + ADC12ON;
	ADC12CTL1 = ADC12SHP + ADC12DIV_7 + ADC12SSEL_3;	// divider /8, SMCLK
	// 8-bit, enable reference out, workaround for bad Vreference (device errata)
	ADC12CTL2 = ADC12RES_0 + ADC12REFOUT;
	// Set interrupt location 1 (ADCMEMO) to use reference and VCC input
	ADC12MCTL0 = ADC12SREF1 + ADC12INCH_10;
	ADC12IE = 0x001;									// Enable interrupt for ADCMEMO
	__delay_cycles (128);								// Delay to allow Ref to settle
	ADC12CTL0 |= ADC12ENC;								// Start single measurement
    ADC12CTL0 |= ADC12SC;                   			// Sampling and conversion start
}

/**
* Start an external measurement to measure the battery voltage using A6.
* 	NOTE: This uses VCC as a reference voltage, you should measure VCC
* 	first to ensure accurate measurement of the battery voltage.
**/
void measureBattery(void)
{
	ADC12CTL0 &= ~ADC12ENC;								// Disable ADC

	ADC12CTL0 = ADC12SHT0_3 + ADC12ON;					// 16 clock ticks sample and hold
	ADC12CTL1 = ADC12SHP + ADC12DIV_7 + ADC12SSEL_3;	// divider /8, SMCLK
	ADC12CTL2 = ADC12RES_0;								// 8-bit resolution
	ADC12MCTL0 = ADC12INCH_6;							// Use input A6 (P6.6)
	ADC12IE = 0x001;									// Enable interrupt for ADCMEMO
	ADC12CTL0 |= ADC12ENC;								// Start single measurement
    ADC12CTL0 |= ADC12SC;                   			// Sampling and conversion start
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
* Send a 8-bit char using the hardware UART
**/
void SendByte_UART(unsigned char txValue)
{
    while (!(UCA0IFG&UCTXIFG));			// USCI_A0 TX buffer ready?
	UCA0TXBUF = txValue;				// Send 8-bit character
}


/**
* UART interrupt. Currently set to only interrupt when a value is received.
**/
#pragma vector=USCI_A0_VECTOR
__interrupt void USCI_A0_ISR(void)
{
	switch(__even_in_range(UCA0IV,4))
	{
		case 0:break;								// Vector 0 - no interrupt
		case 2:										// Vector 2 - RXIFG
			UART_RXData = UCA0RXBUF;				// Received byte to UART_RXData
			StatusRegister |= UART_RX;				// Set the UART_RX flag for the main loop
			__bic_SR_register_on_exit(LPM0_bits);	// Wake-up CPU
			break;
		case 4:break;								// Vector 4 - TXIFG
		default: break;
	}
}

/**
* Button press P2.1 interrupt
**/
#pragma vector=PORT2_VECTOR
__interrupt void Port_2(void)
{
	// Toggle LED when button pressed (for visual indication)
	P1OUT ^= BIT0;
	P2IFG &= ~BIT1;							// P2.1 IFG cleared loop for button press

	StatusRegister |= BUTTON;				// Set the BUTTON flag for the main loop
	__bic_SR_register_on_exit(LPM0_bits);	// Wake-up CPU
}

/**
* ADC12 Interrupt. Only MEM0 is used.
**/
#pragma vector=ADC12_VECTOR
__interrupt void ADC12ISR (void)
{
	switch(__even_in_range(ADC12IV,34))
	{
		case  0: break;							// Vector  0:  No interrupt
		case  2: break;							// Vector  2:  ADC overflow
		case  4: break;							// Vector  4:  ADC timing overflow
		case  6:								// Vector  6:  ADC12IFG0 (MEM0)

			ADCValue = ADC12MEM0;				// Saves measured value to ADCValue.

			// Re-enable the button interrupt (might be disabled for battery measurement).
			P2DIR &= ~BIT1;						// Set P2.1 to input direction
			P2REN |= BIT1;						// Enable P2.1 internal resistance
			P2OUT |= BIT1;						// Set P2.1 as pull-Up resistance
			P2IES |= BIT1;						// Interrupt on P2.1 Hi/lo edge
			P2IFG &= ~BIT1;						// P2.1 IFG cleared
			P2IE |= BIT1;						// P2.1 interrupt enabled

			StatusRegister |= ADC;					// Set ADC flag
			__bic_SR_register_on_exit(LPM0_bits);	// Wake-up CPU
			break;

		case  8: break;							// Vector  8:  ADC12IFG1
		case 10: break;							// Vector 10:  ADC12IFG2
		case 12: break;							// Vector 12:  ADC12IFG3
		case 14: break;							// Vector 14:  ADC12IFG4
		case 16: break;							// Vector 16:  ADC12IFG5
		case 18: break;							// Vector 18:  ADC12IFG6
		case 20: break;							// Vector 20:  ADC12IFG7
		case 22: break;							// Vector 22:  ADC12IFG8
		case 24: break;							// Vector 24:  ADC12IFG9
		case 26: break;							// Vector 26:  ADC12IFG10
		case 28: break;							// Vector 28:  ADC12IFG11
		case 30: break;							// Vector 30:  ADC12IFG12
		case 32: break;							// Vector 32:  ADC12IFG13
		case 34: break;							// Vector 34:  ADC12IFG14
		default: break;
	}
}
