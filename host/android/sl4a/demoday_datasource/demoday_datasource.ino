#define ACCELERATION_SERIAL_PREFIX "acc"
#define BUTTON_SERIAL_PREFIX "btn"

unsigned long sampleSent = 0; //when the sample batches were last sent
unsigned long samplePeriod = 256; //delay in milliseconds between each sample batch

void setup(){
  Serial.begin(115200);
}

void loop(){
  unsigned long now = millis();
  if( (now - sampleSent) > samplePeriod){
    sendButton();
    sendAcceleration();
    sampleSent = now;
  }
}

void sendButton(){
  Serial.print(    BUTTON_SERIAL_PREFIX );
  Serial.println(  getPushed() );
}

void sendAcceleration(){
  Serial.print(    ACCELERATION_SERIAL_PREFIX );
  Serial.print(    getX()  );
  Serial.print(    ","     );
  Serial.print(    getY()  );
  Serial.print(    ","     );
  Serial.println(  getZ()  );
}

//Below this line would be different in a real hardware sketch. Substitute your own functions

boolean fakeButtonPushed = true;

boolean getPushed(){
  if(random(1024) % 8 == 0){
    fakeButtonPushed = ! fakeButtonPushed;
  }
  return fakeButtonPushed;
}

int fakeX=-128, fakeY=-128, fakeZ=-128;

int getX(){
  fakeAxisBehaviour(&fakeX);
  return fakeX;
}

int getY(){
  fakeAxisBehaviour(&fakeY);
  return fakeY;
}

int getZ(){
  fakeAxisBehaviour(&fakeZ);
  return fakeZ;
}

void fakeAxisBehaviour(int *fakeAxis ){
  if(*fakeAxis == -128){ //initialisation condition - set a random starting value
    *fakeAxis = int(random(-127,128));
  }
  *fakeAxis += random(2);
  *fakeAxis -= random(2);
  *fakeAxis = min(128,*fakeAxis);
  *fakeAxis = max(-128,*fakeAxis);

}
