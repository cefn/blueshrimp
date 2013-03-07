/*
 * TODO CH add simpler invocations which do not need an int pointer (which assume that the int pointed to is zero)
*/

#if ARDUINO >= 100
 #include "Arduino.h"
#else
 #include "WProgram.h"
#endif

#include "Code7.h"

Code7::Code7(){
}

/**
Reports the number of encoded bytes needed to represent a given number of unencoded bytes.
 */
int Code7::numEncodedBytes(int numUnencodedBytes){
	return 
		numUnencodedBytes //every unencoded byte requires one 7 bit byte
		+	//and also
		( (numUnencodedBytes + 6 ) / 7 ) //for every seven unencoded bytes (rounding up) an overflow byte is needed
	;
}

/**
Reports the number of unencoded bytes which are represented by a given number of encoded bytes.
 */
int Code7::numDecodedBytes(int numEncodedBytes){
	return 
		numEncodedBytes // the majority of encoded bytes are one-to-one with decoded bytes
		-   //except
		(numEncodedBytes + 7) / 8 //in every group of eight encoded bytes (rounding up) there is an overflow byte    
	;
}

/** Symmetric with decodefrom7 - encodes bytes to 7-bit values, with an overflow byte 
* to store extra bits. Returns the number of total bytes written to the destination byte array*/
int Code7::encodeTo7(byte* srcBytes, int srcCount, byte* dstBytes){
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
* after each frame of 7 bytes (with the final frame potentially being less than 7 bytes). 
* TODO return the number of bytes consumed from the source array, note possible bug in CH comment
* */
void Code7::decodeFrom7(byte* srcBytes, byte* dstBytes, int dstCount){
  int srcPos = 0;
  int partialFrameLength = dstCount % 7; //find out number of bytes stored in last frame (remainder from frames of 7)
  int overflowPos = 0; //keeps track of the next overflow bit to read from the overflow byte 
  for(int dstPos = 0; dstPos < dstCount; dstPos++){
    
    //get the 7 bits from the current byte, and reconstruct the final bit from the overflowbyte
    int frameLength = dstPos + partialFrameLength < dstCount ? 7 : partialFrameLength; //frame length (not including overflow byte)
    dstBytes[dstPos] = srcBytes[srcPos] | ((srcBytes[srcPos - overflowPos + frameLength] << (1 + overflowPos)) & 0x80); //read extra overflow bit from predictably offset overflow byte 
	                                                                                              //(srcPos - overflowPos is the start of the frame)
    overflowPos++; //update overflow read position
    srcPos++; //update src read position
    if(overflowPos == 7){ //TODO CH N.B. until this logic accommodates for frames less than 7 long, the srcPos value is unreliable as a count
      overflowPos = 0;
      srcPos++; //update read position to skip the overflow byte
    }
  }
}

void Code7::writeSignedLong(long value, byte* srcBytes, int* offset){
	//marshal it, forcing big-endian order, changing offset value (passed by reference)
	srcBytes[(*offset)++] = (value >> 24) & 0xFF;
	srcBytes[(*offset)++] = (value >> 16) & 0xFF;
	srcBytes[(*offset)++] = (value >>  8) & 0xFF;
	srcBytes[(*offset)++] = (value      ) & 0xFF;
}

long Code7::readSignedLong(byte* srcBytes, int* offset){
	//unmarshall it, assuming big-endian order, changing offset value (passed by reference)
	long value = 0;
	value |= ((long)srcBytes[(*offset)++]) << 24;
	value |= ((long)srcBytes[(*offset)++]) << 16;
	value |= ((long)srcBytes[(*offset)++]) <<  8;
	value |= ((long)srcBytes[(*offset)++]);
	return value;
}

void Code7::writeUnsignedLong(unsigned long value, byte* srcBytes, int* offset){
	//marshal it, forcing big-endian order, changing offset value (passed by reference)
	srcBytes[(*offset)++] = (value >> 24) & 0xFF;
	srcBytes[(*offset)++] = (value >> 16) & 0xFF;
	srcBytes[(*offset)++] = (value >>  8) & 0xFF;
	srcBytes[(*offset)++] = (value      ) & 0xFF;
}

unsigned long Code7::readUnsignedLong(byte* srcBytes, int* offset){
	//unmarshall it, assuming big-endian order, changing offset value (passed by reference)
	unsigned long value = 0;
	value |= ((unsigned long)srcBytes[(*offset)++]) << 24;
	value |= ((unsigned long)srcBytes[(*offset)++]) << 16;
	value |= ((unsigned long)srcBytes[(*offset)++]) <<  8;
	value |= ((unsigned long)srcBytes[(*offset)++]);
	return value;
}

void Code7::writeSignedInt(int value, byte* srcBytes, int* offset){
	//marshal it, forcing big-endian order, changing offset value (passed by reference)
	srcBytes[(*offset)++] = (value >>  8) & 0xFF;
	srcBytes[(*offset)++] = (value      ) & 0xFF;
}

int Code7::readSignedInt(byte* srcBytes, int* offset){
	//unmarshall it, assuming big-endian order, changing offset value (passed by reference)
	int value = 0;
	value |= ((int)srcBytes[(*offset)++]) << 8;
	value |= ((int)srcBytes[(*offset)++]);
	return value;
}

void Code7::writeUnsignedInt(unsigned int value, byte* srcBytes, int* offset){
	//marshal it, forcing big-endian order, changing offset value (passed by reference)
	srcBytes[(*offset)++] = (value >>  8) & 0xFF;
	srcBytes[(*offset)++] = (value      ) & 0xFF;
}

unsigned int Code7::readUnsignedInt(byte* srcBytes, int* offset){
	//unmarshall it, assuming big-endian order, changing offset value (passed by reference)
	unsigned int value = 0;
	value |= ((unsigned int)srcBytes[(*offset)++]) << 8;
	value |= ((unsigned int)srcBytes[(*offset)++]);
	return value;
}

void Code7::writeByte(byte value, byte* srcBytes, int* offset){
	writeUnsignedChar((unsigned char)value, srcBytes, offset);
}

byte Code7::readByte(byte* srcBytes, int* offset){
	return (byte) readUnsignedChar(srcBytes, offset);
}

void Code7::writeUnsignedChar(unsigned char value, byte* srcBytes, int* offset){
	//marshal it, forcing big-endian order, changing offset value (passed by reference)
	srcBytes[(*offset)++] = (value      ) & 0xFF;
}

unsigned char Code7::readUnsignedChar(byte* srcBytes, int* offset){
	//unmarshall it, assuming big-endian order, changing offset value (passed by reference)
	return ((long)srcBytes[(*offset)++]);
}
