/*
  Code7 library for putting 8-bit bytes and multi-byte values
  into byte arrays, using only 7 bits per byte
  Created by Cefn Hoile
  Released into the public domain.
*/
#ifndef Code7_h

#define Code7_h

#include "Arduino.h"

class Code7
{
  public:
	Code7();
	int encodeTo7(    byte* srcBytes, int srcCount,   byte* dstBytes);
	void decodeFrom7( byte* srcBytes, byte* dstBytes, int dstCount);
	
	void 			writeSignedLong(   long value,           byte* srcBytes, int* offset);
	void 			writeSignedInt(    int value,            byte* srcBytes, int* offset);
	void 			writeUnsignedInt(  unsigned int value,  byte* srcBytes, int* offset);
	void 			writeByte(         byte value,            byte* srcBytes, int* offset);
	void 			writeUnsignedChar( unsigned char value, byte* srcBytes, int* offset);
	
	long 			readSignedLong(    byte* srcBytes, int* offset);
	int 			readSignedInt(     byte* srcBytes, int* offset);
	unsigned int 	readUnsignedInt(   byte* srcBytes, int* offset);
	byte 			readByte(          byte* srcBytes, int* offset);
	unsigned char 	readUnsignedChar(  byte* srcBytes, int* offset);

};

#endif
