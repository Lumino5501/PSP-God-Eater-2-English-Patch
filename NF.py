import os,re,binascii,sys,io
class Br:
	def __init__(self,data):
		self.data = data
	def wpad(self,num):
		pad = num - (self.data.tell() % num or num)
		if pad:
		      self.data.write(b"\x00"*pad)
	def readUint8(self):
		return int.from_bytes(self.data.read(1), byteorder='little', signed=False)
	def readUint16(self):
		return  int.from_bytes(self.data.read(2), byteorder='little', signed=False)
	def readUint32(self):
		return int.from_bytes(self.data.read(4), byteorder='little', signed=False)
	def rl(self,x):
		x = self.data.read(x)
		x = int.from_bytes(x, byteorder="little")
		return x		
	def rb(self,x):
		x = self.data.read(x)
		x = int.from_bytes(x, byteorder='big')
		return x
	def rsf(self,pos,size):
		self.data.seek(pos,0)
		chars = self.data.read(size)
		return chars
	def rsb(self,pos):
		self.data.seek(pos,0)
		chars = b''
		while True:
			c = self.data.read(1)
			chars = chars + c
			if c == b'\x02':
				return chars
	def rs8(self):
		chars = b""
		while True:
			c = self.data.read(1)
			chars+=c
			if c == b"\x00":
				return chars[:-1].decode('utf-8')
	def readString(self):
		chars = ""
		while True:
			c = self.data.read(1).decode("utf-8", 'backslashreplace')
			chars+=c
			if c == chr(0):
				return chars
	def getUtf8(self,offset):
		base = self.data.tell()
		self.data.seek(offset,0)
		chars = b""
		while True:
			c = self.data.read(1)
			chars+=c
			if c == b"\x00":
				self.data.seek(base,0)
				return chars[:-1].decode('utf-8')
	def getUtf16(self,offset):
		base = self.data.tell()
		self.data.seek(offset,0)
		chars = b""
		while True:
			c = self.data.read(2)
			chars+=c
			if c == b"\x00\x00":
				self.data.seek(base,0)
				return chars[:-2].decode('utf-16')
	def getsize(self):
		pos = self.data.tell()
		self.data.seek(0,0)
		size = len(self.data.read())
		self.data.seek(pos,0)
		return size
	def getname(self):
		return os.path.basename(self.data.name)
	def getdata(self):
		self.data.seek(0,0)
		return self.data.read()
	def getBytes(self,pos,size):
		base = self.data.tell()
		self.data.seek(pos,0)
		bin = self.data.read(size)
		self.data.seek(base,0)
		return bin
	def rt(self):
		text = []
		while True :
			c = self.data.readline()
			if c[5:10] == "-----":
				return "".join(text)
			text.append(c)
	def readline(self):
		data = self.data.readline()
		return data
	def seek(self,offset, origin=0):
		self.data.seek(offset,origin)
		return ""
	def tell(self):
		data = self.data.tell()
		return data
	def read(self,x=False):
		if x:
			output = self.data.read(x)
		else:
			output = self.data.read()
		return output
	
	def write(self,indata):
		self.data.write(indata)
		return ""
	def writeUint32(self,x):
		self.data.write(x.to_bytes(4, byteorder='little', signed=False))
	def writeUint16(self,x):
		self.data.write(x.to_bytes(2, byteorder='little', signed=False))
	def writeintB(self,x,y):
		self.data.write(x.to_bytes(y, byteorder="big", signed=False))

	def close(self):
		self.data.close()
		return ""
def fileSave(data,name):
	os.makedirs(os.path.dirname(name), exist_ok=True)
	output = open(name, "wb")
	output.write(data)
