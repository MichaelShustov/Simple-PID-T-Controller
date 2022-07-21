
// User input
int userInput[3];    // raw input from serial buffer, 3 bytes
int startbyte;       // start byte, begin reading input
int i;               // iterator

// LED on Pin 13 for digital on/off demo
int ledPin = 13;
int pinState = LOW;
int chan;
int state;

int analogPin0 = A0; // analog ports to check the line voltage
int analogPin1 = A1;
int analogPin2 = A2;
int analogPin3 = A3;
int analogPin4 = A4;
int analogPin5 = A5;
int analogVal = 0;  // variable to store the value read


void setup() {
  analogWrite(3, 0);
  analogWrite(5, 0);
  analogWrite(6, 0);
  analogWrite(9, 0);
  analogWrite(10, 0);
  analogWrite(11, 0);
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);

  // Open the serial connection, 9600 baud
  Serial.begin(9600);
}

void loop() 
{ 
  // Wait for serial input (min 3 bytes in buffer)
  if (Serial.available() > 2) {
    // Read the first byte
    startbyte = Serial.read();
    
    // If it's the startbyte 253 - send comand to PWM pin
    if (startbyte == 0xfd) {
      // ... then get the next two bytes
      
      
      for (i=0;i<2;i++) {
        userInput[i] = Serial.read();
      }
      // First byte = digital channel?
      chan = userInput[0];
      // Second byte state?
      state = userInput[1];
      
      pinState = 0;
      if (state >= 0 && state <=255) { pinState = state;}

      analogWrite(chan, pinState);
      
    
    }
    // if it is the startbyte 252 - measure analog channel and send back to Serial
    if (startbyte == 0xfc){

      
      for (i=0;i<2;i++) {
        userInput[i] = Serial.read();
      }
      // First byte = analog channel?
      chan = userInput[0];
      // Second byte can be any number, it is not in use here
      state = userInput[1]; 

      if ((chan < 0) || (state > 5)) { chan = 0;}

      if (chan == 0) {analogVal = analogRead(analogPin0);}
      if (chan == 1) {analogVal = analogRead(analogPin1);}
      if (chan == 2) {analogVal = analogRead(analogPin2);}
      if (chan == 3) {analogVal = analogRead(analogPin3);}
      if (chan == 4) {analogVal = analogRead(analogPin4);}
      if (chan == 5) {analogVal = analogRead(analogPin5);}

      //Serial.println(analogVal);
      
      Serial.print(analogVal);
      
      // analogWrite(13, 0);

      
    }
    
  }
}
























