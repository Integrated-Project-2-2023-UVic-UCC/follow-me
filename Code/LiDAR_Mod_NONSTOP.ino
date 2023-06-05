const int BUFFER_SIZE = 4; //for the received data
char buf[BUFFER_SIZE];

//Definicions de pins
const int DIR_MOTOR1 = 5; //pin outs for the stepper motors
const int STEP_MOTOR1 = 18;
const int DIR_MOTOR2 = 0;
const int STEP_MOTOR2 = 4;

unsigned int dist; //received data distance

float theta; //received data angle 

int pulse1 = 0; //that variable is to control the amount of steps each motor do on a turn

unsigned long previousMillis1 = 0;  //will last time
unsigned long currentMillis1 = 0;   //will store current time

unsigned long previousMillis2 = 0;  //will store last time
unsigned long currentMillis2 = 0;   //will store current time



void setup() {
  Serial.begin(115200);
  Serial.setTimeout(10);
  //Motor 1
  pinMode(STEP_MOTOR1, OUTPUT); //step motor1 and his direction
  pinMode(DIR_MOTOR1, OUTPUT);

  //Motor 2
  pinMode(STEP_MOTOR2, OUTPUT);//step motor2 and his direction
  pinMode(DIR_MOTOR2, OUTPUT);

  digitalWrite(DIR_MOTOR1, HIGH);
  digitalWrite(DIR_MOTOR2, LOW);
}


unsigned long stepper_time = 0;
//unsigned long stepper_time1 = 0;
//unsigned long stepper_time2 = 0;
float stepper_freq = 0;
//float stepper_freq_1 =0;
//float stepper_freq_2 =0;

void loop() {

  if (Serial.available() > 0) {

    int rlen = Serial.readBytes(buf, BUFFER_SIZE); //read bytes from serial port
    if (rlen != BUFFER_SIZE) {
      return;
    }

    // prints the received data
    //Serial.print("I received: ");
    int th = buf[0] + (buf[1] << 8); //0 - 1 for distance
    dist = buf[2] + (buf[3] << 8); // 2 - 3 for angle

    theta = ((float)th) / 100; //scale the angle units

    //Serial.print(dist);
  }

  long set_pt = 0; //thats for the proportional speed - distance
  long err = dist - set_pt;
  if (err < 0) {
    stepper_freq = 0;
  } else if (err > 2000) {
    stepper_freq = 0;
  } else {
    stepper_freq = (float)err / 2000000.0;
  }

  stepper_freq = stepper_freq < 0.32e-3 ? 0 : stepper_freq; // below 0.3e-3 stepper_freq = 0
  stepper_freq = stepper_freq > 0.7e-3 ? 0.7e-3 : stepper_freq; //over 0.7e-3 stepper freq = 0.7e-3

  stepper_time = 1.0 / stepper_freq;

  if (stepper_freq > 0.0) {

//Here are the motor controls,
//it can be seen that there is an offset, so the center of the sensor is not 180º,
//and thats why the left and right turns are 4 degrees out of 180º +- 10º

    if (theta < 178.0) { //turn left

      currentMillis1 = micros();
      if (currentMillis1 - previousMillis1 >= stepper_time) {
        digitalWrite(STEP_MOTOR2, HIGH);
        pulse1 += 1;//to do the turn i restrict the half of the steps from one motor
        if (pulse1 >= 2) {
          digitalWrite(STEP_MOTOR1, HIGH);
        }
        previousMillis1 = currentMillis1;
      }

      currentMillis2 = micros();
      if (currentMillis2 - previousMillis2 >= stepper_time*2) {
        digitalWrite(STEP_MOTOR2, LOW);
        if (pulse1 >= 3) {
          digitalWrite(STEP_MOTOR1, LOW);
          pulse1 = 0;
        }
        previousMillis2 = currentMillis2;
        
        
      }
    }

    else if (theta > 190.0) { //turn right
       currentMillis1 = micros();
      if (currentMillis1 - previousMillis1 >= stepper_time) {
        digitalWrite(STEP_MOTOR1, HIGH);
        pulse1 += 1;//to do the turn i restrict the half of the steps from one motor
        if (pulse1 >= 2) {
          digitalWrite(STEP_MOTOR2, HIGH);
        }
        previousMillis1 = currentMillis1;
      }

      currentMillis2 = micros();
      if (currentMillis2 - previousMillis2 >= stepper_time*2) {
        digitalWrite(STEP_MOTOR1, LOW);
        if (pulse1 >= 3) {
          digitalWrite(STEP_MOTOR2, LOW);
          pulse1 = 0;
        }
        previousMillis2 = currentMillis2;
        
      }
    }


    else { //go straight
      currentMillis1 = micros();
      if (currentMillis1 - previousMillis1 >= stepper_time) {
        digitalWrite(STEP_MOTOR1, HIGH);
        digitalWrite(STEP_MOTOR2, HIGH);
        previousMillis1 = currentMillis1;
      }
      
      currentMillis2 = micros();
      if (currentMillis2 - previousMillis2 >= stepper_time*2) {
        digitalWrite(STEP_MOTOR1, LOW);
        digitalWrite(STEP_MOTOR2, LOW);
        previousMillis2 = currentMillis2;
      }
    }

    //digitalWrite(STEP_MOTOR1, HIGH);
    //digitalWrite(STEP_MOTOR2, HIGH);
    //delayMicroseconds(stepper_time);

    //digitalWrite(STEP_MOTOR1, LOW);
    //digitalWrite(STEP_MOTOR2, LOW);
    //delayMicroseconds(stepper_time);
  }
}
