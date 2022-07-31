
// User input for servo and position
int userInput[3];    // raw input from serial buffer, 3 bytes
int startbyte;       // start byte, begin reading input
int i;               // iterator

// LED on Pin 13 for digital on/off demo
int ledPin = 13;
int pinState = LOW;
int chan;
int state;


void setup() {
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(12, OUTPUT);

  digitalWrite(2, LOW);
  digitalWrite(3, LOW);
  digitalWrite(4, LOW);
  digitalWrite(5, LOW);
  digitalWrite(6, LOW);
  digitalWrite(7, LOW);
  digitalWrite(12, LOW);

  // Open the serial connection, 9600 baud
  Serial.begin(9600);
}

void loop() 
{ 
  // Wait for serial input (min 3 bytes in buffer)
  if (Serial.available() > 2) {
    // Read the first byte
    startbyte = Serial.read();
    // If it's really the startbyte (254) ...
    if (startbyte == 0xfe) {
      // ... then get the next two bytes
      
      
      for (i=0;i<2;i++) {
        userInput[i] = Serial.read();
      }
      // First byte = digital channel?
      chan = userInput[0];
      // Second byte = on/off 1/0?
      state = userInput[1];
      
      
      if (state == 0) { pinState = LOW;}
      else {pinState = HIGH;}

      digitalWrite(chan, state);
    
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

            
      Serial.print(analogVal);
      
     

      
    }


    
  }
}
























