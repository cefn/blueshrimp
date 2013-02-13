/*
Tries to decode a series of Long numbers and sends them back 
as Sprintf-formatted strings to prove correct processing between
Python and Arduino side

Exhaustive processing of the address space, assuming it's bounded by the (inefficiently coded) 
receiving serial link is roughly...

Worst case ascii number length 11 bytes = 11 x 8 bits
Numbers tested per second in worst case 1309
Total time to test address space
2147483648 × 2 / 1309 = 911 hours

Have tested with random number assignment for several hours.

 */
 
 
 
#define DECODED_LENGTH 4
#define ENCODED_LENGTH 5

static char stringBuffer[50];
 
void setup() {
  Serial.begin(115200);  
}

void loop() {
  
  // read in the data
  byte encodedData[ENCODED_LENGTH];
  
  if(Serial.readBytesUntil('\n',(char*)encodedData,ENCODED_LENGTH) > 0){

    //decode it
    byte decodedData[DECODED_LENGTH];
    decodeFrom7(encodedData,decodedData,DECODED_LENGTH);
    
    //unmarshall it, assuming big-endian order
    long unmarshalledLong = 0;
    unmarshalledLong |= decodedData[0] << 24;
    unmarshalledLong |= decodedData[1] << 16;
    unmarshalledLong |= decodedData[2] << 8;
    unmarshalledLong |= decodedData[3] ;
  
    //treat the bytes as a long and print them back 
    sprintf (stringBuffer, "%ld %i %i %i %i\r\n", unmarshalledLong, decodedData[0], decodedData[1],decodedData[2],decodedData[3]);
    Serial.write(stringBuffer);
  
  }

}

void flash(){
  digitalWrite(13, HIGH);   // set the LED on
  delay(100);              // wait for 100
  digitalWrite(13, LOW);    // set the LED off
  delay(100);              // wait for 100
}

/** Symmetric with decodefrom7 - encodes bytes to 7-bit values, with an overflow byte 
* to store extra bits. Returns the number of total bytes written to the destination byte array*/
int encodeTo7(byte* srcBytes, byte* dstBytes, int srcCount){
  byte overflowByte = 0;
  byte overflowPos = 0;
  int dstPos = 0; //current writing position in dst array
  for(int srcPos = 0; srcPos < srcCount; srcPos++){
    
    //store msb in overflowByte, filling bits from left, shifting one extra to avoid msb
    overflowByte |= (srcBytes[srcPos] & 0x80) >> (overflowPos + 1); //store msb in overflow byte using next free position
    overflowPos++; //update overflow write position
    
    //passthrough the 7-bit truncated byte filling destination array from left
    dstBytes[dstPos] = srcBytes[srcPos] & ~0x80; //write the 7 allowed bits (zeroing the msb)
    dstPos++;//update destination write position

    //write overflow byte to stream when it's full or stream is ending
    if(overflowPos == 7 || srcPos == srcCount-1){ //byte full or stream ended
      dstBytes[dstPos] = overflowByte; //write the 7 allowed bits
      dstPos++; //update destination write position
      overflowByte = 0; //reset overflow byte
      overflowPos = 0; //start writing from beginning again
    }
  }
  return dstPos;
}

/** Should be symmetric with encodeTo7(). It populates the specified number of output bytes by reading
* 7 bits from each source byte and retrieving the extra bit from a 7-bit overflow byte which is written after 
* after each frame of 7 bytes (with the final frame potentially being less than 7 bytes). */
void decodeFrom7(byte* srcBytes, byte* dstBytes, int dstCount){
  int srcPos = 0;
  int partialFrameLength = dstCount % 7; //find out number of bytes stored in last frame (remainder from frames of 7)
  //int srcCount = ((dstCount / 7) * 8) + (partialFrameLength == 0 ? 0 : partialFrameLength + 1); //count of source bytes needed
  int overflowPos = 0; //keeps track of the next overflow bit to read from the overflow byte 
  for(int dstPos = 0; dstPos < dstCount; dstPos++){
    
    //get the 7 bits from the current byte, and reconstruct the final bit from the overflowbyte
    int frameLength = dstPos + partialFrameLength < dstCount ? 7 : partialFrameLength; //frame length (not including overflow byte)
    dstBytes[dstPos] = srcBytes[srcPos] | ((srcBytes[srcPos - overflowPos + frameLength] << (1 + overflowPos)) & 0x80); //read extra overflow bit from predictably offset overflow byte 
                                                                                                      //(srcPos - overflowPos is the start of the frame)
    overflowPos++; //update overflow read position
    srcPos++; //update src read position
    if(overflowPos == 7){
      overflowPos = 0;
      srcPos++; //update read position to skip the overflow byte
    }
  }
}

