
byte UART_RX_data;

int LED = 13;

void setup() {
  pinMode(LED, OUTPUT);
  
  // Turn the Serial Protocol ON
  Serial.begin(9600);
}

void loop() {
   /*  check if data has been sent from the computer: */
  if (Serial.available()) {
    /* read the most recent byte */
    UART_RX_data = Serial.read();
    
    // Toggle LED
    if (UART_RX_data == 0x31) {
      digitalWrite(LED, !digitalRead(LED));
    }
    // Hello World
    else if (UART_RX_data == 0x32) {
      Serial.print("Hello world!\n");
    }
    // Author Info
    else if (UART_RX_data == 0x33) {
      Serial.print("NJC from http://store.hardwarebreakout.com!\n");
    }
  }
}
