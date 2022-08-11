char recvdChar;
boolean recvd = false;
int trig_pulse = 5;  // green
int read_pulse = 7;  // yellow
int trig_sham = 4;  // orange
int read_sham = 6;  // blue


void setup() {
  // Open serial connection
  Serial.begin(115200);
  Serial.println("Device ready");

  // Set both trig pins as output
  pinMode(trig_1, OUTPUT);
  pinMode(trig_2, OUTPUT);
  // Set both read pins as input
  pinMode(read_1, INPUT_PULLUP);
  pinMode(read_2, INPUT_PULLUP);
}


void loop() {
  /* Read data from PC */
  recvcommand();
  
  /* Send to TMS */
  sendcommand();
}


void recvcommand() {
  /* Read serial buffer if it has anything */
  if (Serial.available()) {
    recvdChar = Serial.read();
    Serial.println(recvdChar);
    recvd = true;
  }
}


void sendcommand() {
  int count = 0;
  /* If we have new data to send */
  if (recvd == true) {
    /* Determine target pin from command */
    switch (recvdChar) {
      case '1':
        // Trigger a TMS pulse;
        digitalWrite(trig_1, HIGH);
        Serial.println("Pulse sent");
        // Wait until the read pin goes high, signalling a trigger
        while (digitalRead(read_1) == LOW && count < 1000) {
          Serial.println("Waiting for read...");
          Serial.print(count);
          count++;
          continue;
        }
        // Turn off trigger pin
        digitalWrite(trig_1, LOW);
        Serial.println("Pulse completed");
        count = 0;
        break;
        
      case '2':
        // Trigger a TMS pulse;
        digitalWrite(trig_2, HIGH);
        Serial.println("Pulse sent");
        // Wait until the read pin goes high, signalling a trigger
        while (digitalRead(read_2) == LOW && count < 1000) {
          Serial.println("Waiting for read...");
          Serial.print(count);
          count++;
          continue;
        }
        // Turn off trigger pin
        digitalWrite(trig_2, LOW);
        Serial.println("Pulse completed");
        count = 0;
        break;
    }
    // Set recvd back to false, wait for next command
    recvd = false;
  }
}
