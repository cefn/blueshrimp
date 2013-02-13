# writes a Big-endian long value into the destination array, optionally at the given offset, 
# extending the array if offset==length this procedure is suitable for embedding a long into 
# a series of bytes to be encoded
def marshall_long(value, dstbytes, offset=0):
	marshalled_bytes = [
		(value >> 24) & 0xFF, 
		(value >> 16) & 0xFF, 
		(value >>  8) & 0xFF, 
		(value      ) & 0xFF
	]
	dstindex = offset
	dstlength = len(dstbytes)
	for index in range(len(marshalled_bytes)) :
		if dstindex < dstlength :
			dstbytes[dstindex] = marshalled_bytes[index]
		elif dstindex == dstlength:
			dstbytes.append(marshalled_bytes[index])
			dstlength += 1
		else:
			raise BufferError("Tried to write at position " + str(dstindex) + " in destination buffer of length " + str(dstlength) )
		dstindex += 1	
		
# reads a Big-endian long value from the source array, starting from byte zero if no offset is given
# this procedure is suitable for extracting a long from a series of decoded bytes
def unmarshall_long(srcbytes, offset=0):
	dstlong = 0
	dstlong |= srcbytes[offset+0] << 24
	dstlong |= srcbytes[offset+1] << 16
	dstlong |= srcbytes[offset+2] << 8
	dstlong |= srcbytes[offset+3]
	return dstlong
	
def serialize_bytes(srcbytes):
	return ''.join(chr(entry) for entry in srcbytes)

# returns the bytes encoded see canonical Arduino code for comments - this is a port
def encode7(srcbytes):
	
	dstbytes = []
	overflowbyte = 0
	overflowpos = 0
	dstpos = 0
	
	for srcpos, srcbyte in enumerate(srcbytes):	
		srcbyte = srcbyte
		
		overflowbyte |= (srcbyte & 0x80) >> (overflowpos + 1)
		overflowpos += 1
		
		dstbytes.append(srcbyte & ~0x80)
		dstpos += 1
	
		if(overflowpos == 7 or srcpos == len(srcbytes) - 1):
			dstbytes.append(overflowbyte);
			dstpos += 1
			overflowbyte = 0
			overflowpos = 0
	
	return dstbytes
	
# returns the bytes decoded, see canonical Arduino code for comments - this is a port
def decode7(srcbytes, dstcount):
	
	dstbytes = []
	srcpos = 0
	partialframelength = srcbytes.length % 8
	if(partialframelength != 0):
		partialframelength -= 1
	
	overflowpos = 0
	
	for dstpos in range(dstcount):
		framelength = 7 if (dstpos + partialframelength < dstcount) else partialframelength 
		dstbytes.push(srcbytes[srcpos] | ((srcbytes[srcpos - overflowpos + framelength] << (1 + overflowpos)) | 0x80))
		overflowpos += 1
		srcpos += 1
		if(overflowpos == 7):
			overflowpos = 0
			srcpos += 1

	return dstbytes
