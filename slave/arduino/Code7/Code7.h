/*
  Code7 library for putting 8-bit bytes and multi-byte values
  into byte arrays, using only 7 bits per byte
  Created by Cefn Hoile
  Released into the public domain.
*/
#ifndef Code7_h

#define Code7_h

#if ARDUINO >= 100
 #include "Arduino.h"
#else
 #include "WProgram.h"
#endif

class Code7
{
  public:
	Code7();
	int encodeTo7   ( byte*, int  , byte*);
	void decodeFrom7( byte*, byte*, int  );
	
	int numEncodedBytes(int);
	int numDecodedBytes(int);
	
	void 			writeSignedLong(   long,           byte*,  int* offset);
	void 			writeSignedInt(    int ,           byte*,  int* offset);
	void 			writeUnsignedInt(  unsigned int,  byte*,  int* offset);
	void 			writeByte(         byte,            byte*,  int* offset);
	void 			writeUnsignedChar( unsigned char, byte*,  int* offset);
	
	long 			readSignedLong(    byte*, int*);
	int 			readSignedInt(     byte*, int*);
	unsigned int 	readUnsignedInt(   byte*, int*);
	byte 			readByte(          byte*, int*);
	unsigned char 	readUnsignedChar(  byte*, int*);

};

#endif
