from Crypto.Cipher import AES
import binascii

def padPKCS7(s, size):
	pad = size - len(s)%size
	if pad == 0 :
		return s + bytes([size] * size)
	return s + bytes([pad] * pad)

class Error(Exception):
	pass

class BadPaddingError(Error):
	pass


def stripPKCS7(s,size=16):
	
	padding_len = s[-1]

	if padding_len > size or padding_len == 0x00:
		#print(s)
		raise BadPaddingError

	slen = len(s)
	padding = s[slen - padding_len:slen]
	for x in padding:
		if x != padding_len:
			#print(s)
			raise BadPaddingError
	
	return s[:slen-padding_len]


def ecb_encrypt(s,key):
	size = len(key)
	s = padPKCS7(s,size)
	
	blocks = get_blocks(s,size)
	
	cipher = AES.new(key,AES.MODE_ECB)
	
	cipherText = b''
	for i in range(len(blocks)):
		cipherText = cipherText + cipher.encrypt(blocks[i])

	return cipherText	

def ecb_decrypt(s,key):
	
	size = len(key)
	cipherBlocks = get_blocks(s,size)
	
	cipher = AES.new(key, AES.MODE_ECB)

	plainText = b''
	for i in range(len(blocks)):
		plainText = plainText + cipher.decrypt(cipherBlocks[i])

	return plainText

def cbc_encrypt(s,k, iv=b''):

	cipher = AES.new(k, AES.MODE_ECB)
	size = len(k)
	x = padPKCS7(s,size)
	blocks = get_blocks(x, size)
	cipherBlocks = [None] * (len(blocks) + 1)
	cipherBlocks[0] = iv

	for i in range(len(blocks)):
		cipherBlocks[1+i] = cipher.encrypt(XORBlocks(blocks[i], cipherBlocks[i]))

	cipherText = b''
	for i in range(len(blocks)):
		cipherText += cipherBlocks[1+i]

	return cipherText	

def cbc_decrypt(y,k, iv=b''):
	cipher = AES.new(k, AES.MODE_ECB)
	size = len(k)
	blocks = get_blocks(y, size)
	plainBlocks = [None] * len(blocks)

	plainBlocks[0] = XORBlocks(iv, cipher.decrypt(blocks[0]))

	for i in range(1,len(blocks)):
		plainBlocks[i] = XORBlocks(blocks[i-1], cipher.decrypt(blocks[i]))

	plainText = b''
	for i in range(len(blocks)):
		plainText += plainBlocks[i]
	
	return stripPKCS7(plainText,size)

def XORBlocks(b1,b2):
	return bytes([x^y for x,y in zip(b1,b2)])

def get_blocks(s, blocksize=16):
	return [s[i:i+blocksize] for i in range(0, len(s), blocksize)]

def union_blocks(blocks):
	out = b''
	for b in blocks:
		out += b

	return out
	

def main():
	test_padding()
	test_cbc()
	s = b'a'*16 + b'b'*16 + b'c'*16 + b'd'*16
	print(s == union_blocks(get_blocks(s)))

def test_cbc():
	s = b'abcd' * 4 * 10 + b'a'
	iv = b'\x42\x43\x44\x45\x42\x43\x44\x45\x42\x43\x44\x45\x42\x43\x44\x45' 
	key = iv
	y = cbc_encrypt(s,key,iv)
	x = cbc_decrypt(y,key,iv)
	print(x)


def test_padding():
	s = b'ICE ICE BABY'
	x = padPKCS7(s,16)
	assert(stripPKCS7(x) == b'ICE ICE BABY')

	s = b'a'*16
	spad = s + b'\x10' * 16
	x = padPKCS7(s,16)
	assert(x == spad)
	assert(stripPKCS7(x) == s)

	bad1 = b'ICE ICE BABY\x05\x05\x05\x05'
	bad2 = b'ICE ICE BABY\x01\x02\x03\x04'

	try:
		stripPKCS7(bad1,16)
	except BadPaddingError:
		pass
	try:
		stripPKCS7(bad2,16)
	except BadPaddingError:
		pass

	

	print("PaddingTest Passed")
	return True

#main()
