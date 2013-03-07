import struct

# Returns the number of 7-bit encoded bytes which correspond 
# to a given number of 8-bit unencoded bytes
def num_encoded_bytes(num_unencoded):
	return (
				num_unencoded  # every unencoded byte requires one 7 bit byte
				+  # also
				( (num_unencoded + 6 ) // 7 )  # for every seven unencoded bytes (rounding up) an overflow byte is needed
	)  

# Returns the number of 8-bit unencoded bytes which correspond 
# to a given number of 7-bit encoded bytes
def num_unencoded_bytes(num_encoded):
	if(num_encoded % 8 == 1):
		raise Error("Number of bytes modulo 8 is 1. No valid code7 frame can be 1 byte long")
	else:
		return (
		 num_encoded  # the majority of encoded bytes are one-to-one with decoded bytes
		 -  # except
		 (num_encoded + 7) // 8  # in every group of eight encoded bytes (rounding up) there is an overflow byte
		)

# writes a Big-endian 32-bit long value into the destination array, optionally at the given offset, 
# extending the array if offset==length 
# this procedure is suitable for embedding a long into 
# a series of bytes to be encoded
def marshall_long(value, dstbytes=[], offset=0):
	# extract bytes from long 
	marshalled_bytes = [
		(value >> 24) & 0xFF, 
		(value >> 16) & 0xFF, 
		(value >>  8) & 0xFF, 
		(value      ) & 0xFF
	]
	# push the bytes into the destination array, extending as necessary
	dstindex = offset
	dstlength = len(dstbytes)
	for index in range(len(marshalled_bytes)) :
		if dstindex < dstlength : # within destination array - reusing byte positions
			dstbytes[dstindex] = marshalled_bytes[index]
		elif dstindex == dstlength: # at end of destination array - add a new byte position
			dstbytes.append(marshalled_bytes[index])
			dstlength += 1
		else: # beyond destination array - cannot guess at values to fill buffer with - hard fail
			raise BufferError("Tried to write at position " + str(dstindex) + " in destination buffer of length " + str(dstlength) )
		dstindex += 1
	return dstbytes
		
# reads a Big-endian long value from the source array, starting from byte zero if no offset is given
# this procedure is suitable for extracting a long from a series of decoded bytes
# TODO CH consider use of struct module to normalise marshalling and unmarshalling as per unmarshall_unsigned_long(...)
# TODO CH how will non-specialists know how many bytes were 'used up' from the srcbytes array?
def unmarshall_long(srcbytes, offset=0):
	dstlong = 0
	# untyped srcbytes sanitised by enforcing values < 255 by oring with 0xFF
	dstlong |= (srcbytes[offset+0] & 0xFF)  << 24
	dstlong |= (srcbytes[offset+1] & 0xFF)  << 16
	dstlong |= (srcbytes[offset+2] & 0xFF)  << 8
	dstlong |= (srcbytes[offset+3] & 0xFF)
	return dstlong
	
# reads a Big-endian long value from the source array, starting from byte zero if no offset is given
# this procedure is suitable for extracting a long from a series of decoded bytes
def unmarshall_unsigned_long(srcbytes, offset=0):
	return struct.unpack('>L', str(bytearray(srcbytes[offset:offset+4]))) # there are 4 bytes in an unsigned long

# transforms a series of numerical byte values into a string of ascii characters
# to satisfy python's type requirements
def serialize_bytes(srcbytes):
	return ''.join(chr(entry) for entry in srcbytes)

# returns the bytes encoded see canonical Arduino code for comments - this is a port
def encode7(srcbytes):

	dstbytes = []
	overflowbyte = 0
	overflowpos = 0

	for srcpos, srcbyte in enumerate(srcbytes):	

		overflowbyte |= (srcbyte & 0x80) >> (overflowpos + 1)
		overflowpos += 1

		dstbytes.append(srcbyte & ~0x80)

		if(overflowpos == 7 or srcpos == len(srcbytes) - 1):
			dstbytes.append(overflowbyte);
			overflowbyte = 0
			overflowpos = 0

	return dstbytes

# returns the bytes decoded, see canonical Arduino code for comments - this is a port
def decode7(srcbytes):	
	lastpos = len(srcbytes) - 1              # absolute index of last byte
	framestart = 0                           # byte at beginning of current 8-byte frame
	framepos = 0                             # next byte to be read in current frame
	dstbytes = []                            # destination array for decoded bytes
	while (framestart + framepos) < lastpos:
		overflowpos = (lastpos % 8) if (framestart // 8 == lastpos // 8) else 7  # last byte is overflow when final frame foreshortened
		dstbytes.append( srcbytes[framestart + framepos] | ((srcbytes[framestart + overflowpos] << (1 + framepos)) & 0x80) )
		framepos += 1
		if(framepos == overflowpos):  # roll over to next frame, resetting overflow values
			framestart += 8
			framepos = 0
	return dstbytes
