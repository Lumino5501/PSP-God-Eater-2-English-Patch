from NF import *
from LISTFILE import LISTFILE
from TEXTURE_INJECTOR import *
import zlib,os
from time import sleep
def blz_com(data ,dsize):
	f = Br(io.BytesIO(data))
	def compress_chunk(size):
		deflate_compress = zlib.compressobj(9, zlib.DEFLATED, -15)
		data = deflate_compress.compress(f.read(size)) + deflate_compress.flush()
		chunksize = len(data).to_bytes(2, byteorder='little', signed=False)
		data = chunksize + data
		return data
#---------------------
	deflate_compress = zlib.compressobj(9, zlib.DEFLATED, -15)
	tail_size = dsize%0xffff
	number_part = dsize//0xffff
#---------------------
	if dsize < 0xffff:
		compressed = None
		compressed = deflate_compress.compress(f.read()) + deflate_compress.flush()
		chunksize = len(compressed).to_bytes(2, byteorder='little', signed=False)
		compressed = b"blz2" + chunksize  + compressed
		return compressed
#---------------------
	else :
		compressed  =b""
		i=0
		head= compress_chunk(tail_size)
		compressed = compressed + head
		while i <number_part-1 :
			chunk = compress_chunk(0xffff)
			compressed = compressed + chunk
			i+=1
		last_chunk = compress_chunk(0xffff)
		compressed = b'blz2' + last_chunk + compressed
		return compressed

def blz(data, csize,dsize):
	data = Br(io.BytesIO(data))
	magic = data.read(4)
	if magic != b"blz2":
		return data.getdata()
	decom = b''
	if dsize >=0xffff:
		size = data.readUint16()
		ekor = zlib.decompress(data.read(size),-15)
		while True:
			size = data.readUint16()
			decom +=zlib.decompress(data.read(size),-15)
			if data.tell()== csize:
				data.close()
				return decom+ekor

	else:
		size = data.readUint16()
		decom = zlib.decompress(data.read(size),-15)
		data.close()
		return decom
		
class Tr2:
	def __init__(self,data,folder,name):
		self.data = Br(io.BytesIO(data))
		self.folder = folder
		self.name = name[:-4]
	def unpack(self):
		f = self.data
		folder = self.folder
		ext = f.read(4)
		unk0= f.read(4)
		trname = f.rs8()
		f.seek(0x38,0)
		unk1 = f.read(4)
		totalFile = f.readUint32()
		for i in range(totalFile):
			num = f.readUint32()
			off =  f.readUint32()
			unk2 = f.read(4)
			comSize = f.readUint32()
			decSize = f.readUint32()
			bText = Br(io.BytesIO(f.getBytes(off,comSize)))
			textName = bText.rs8()
			bText.seek(0x38,0)
			yobi = bText.read(4).replace(b"\x00",b"").decode("utf-8")
			bText.read(4)
			textEncoding = bText.rs8()
			if (textEncoding == "UTF-8") or (textEncoding == "UTF-16LE"):
				strings = Br(io.StringIO(""))
				bText.seek(0x7c,0)
				stringTotal = bText.readUint32()
				strings.write("NOTE:\n------------------------------\nTOTAL_STRING:{0:04d}\n====================\n".format(stringTotal))
				for i in range(stringTotal):
					if yobi:
						bText.read(4)
						offString = bText.readUint32()
						lenString = bText.readUint32()
					else:
						offString = bText.readUint32()
					if textEncoding == "UTF-8":
						string = bText.getUtf8(offString)
					elif textEncoding == "UTF-16LE":
						string = bText.getUtf16(offString)
					strings.write("[{0:04d}]\n{1}\n------------------------------\n".format(i,string))
				fileSave(strings.getdata().encode("utf-8"),"{0}{1:04d}_{2}/{3}.txt".format(folder,numTxt,self.name,textName))
	def repack(self):
		f = self.data
		folder = self.folder
		ext = f.read(4)
		unk0= f.read(4)
		trname = f.rs8()
		f.seek(0x38,0)
		unk1 = f.read(4)
		totalFile = f.readUint32()
		f.read(4)
		basePtr = f.readUint32()
		f.seek(0x40,0)
		newFiles = Br(io.BytesIO())
		ptr = Br(io.BytesIO(f.getBytes(0x40,(totalFile*20))))
		for i in range(totalFile):
			newOffFile = newFiles.tell()+basePtr
			num = ptr.readUint32()
			offFile =  ptr.readUint32()
			unk2 = ptr.read(4)
			comSize = ptr.readUint32()
			decSize = ptr.readUint32()
			bText = Br(io.BytesIO(f.getBytes(offFile,comSize)))
			textName = bText.rs8()
			bText.seek(0x38,0)
			yobi = bText.read(4).replace(b"\x00",b"").decode("utf-8")
			bText.read(4)
			textEncoding = bText.rs8()
			if (textEncoding == "UTF-8") or (textEncoding == "UTF-16LE"):
				newTxt = Br(open("{0}/{1:04d}_{2}/{3}.txt".format(folder,numTxt,self.name,textName), "r",encoding="utf-8"))
				newStrings = Br(io.BytesIO())
				#print(textEncoding)
				bText.seek(0x7c,0)
				stringTotal = bText.readUint32()
				note = newTxt.rt()
				total = newTxt.readline()
				newTxt.readline()
				if yobi:
					bText.read(4)
					baseString = bText.readUint32()
					#print(baseString)
					bText.seek(-8,1)
				else:
					baseString = bText.readUint32()
					bText.seek(-4,1)
				for i in range(stringTotal):
					number = newTxt.readline()[1:-2]
					if textEncoding == "UTF-8":
						newString = newTxt.rt()[:-1].encode("utf-8")
						newOffstring = newStrings.tell()+baseString
						newLenString = len(newString)
						newStrings.write(newString + b"\x00")
					elif textEncoding == "UTF-16LE":
						newString = newTxt.rt()[:-1].encode("utf-16")[2:]
						newOffstring = newStrings.tell()+baseString
						newLenString = len(newString)
						newStrings.write(newString + b"\x00\x00")
					if yobi:
						bText.read(4)
						bText.writeUint32(newOffstring)
						bText.writeUint32(newLenString)
					else:
						bText.writeUint32(newOffstring)
						bText.writeUint32(newStrings.tell()+baseString)
						bText.seek(-4,1)
				pad = 16 - (newStrings.tell() % 16 or 16)
				newStrings.write(b"\x00"*pad)
				newBText = bText.getBytes(0,baseString)+newStrings.getdata()
				newComsize,newDecsize = len(newBText),len(newBText)
			else:
				newBText = bText.getdata()
				newComsize,newDecsize = comSize,decSize
			#WRITE NEWFILE+PTR
			f.read(4)
			f.writeUint32(newOffFile)
			f.read(4)
			f.writeUint32(newComsize)
			f.writeUint32(newDecsize)
			newFiles.write(newBText)
		return f.getBytes(0,basePtr)+newFiles.getdata()
class Kst:
	def __init__(self,data,folder,name):
		self.data = Br(io.BytesIO(data))
		self.folder = folder
		self.name = name
	def unpack(self):
		folder = self.folder
		if self.name == "article.kst":
			f = self.data
			strings = Br(io.StringIO(""))
			strings.write("NOTE:\n------------------------------\nTOTAL_STRING:{0:04d}\n====================\n".format(4873))
			f.seek(0x39740,0)
			for i in range(4873):
				lin = f.readUint16()
				pad = (lin%2)
				if pad:
					lin+=pad
				string = f.read(lin).replace(b"\x00",b"").decode("utf-8")
				strings.write("[{0:04d}]\n{1}\n------------------------------\n".format(i,string))
			fileSave(strings.getdata().encode("utf-8"),"{0}{1:04d}_{2}/{3}.txt".format(folder,numTxt,self.name[:-4],self.name[:-4]))
		elif self.name == "article_ex.kst":
			f = self.data;
			strings = Br(io.StringIO(""))
			strings.write("NOTE:\n------------------------------\nTOTAL_STRING:{0:04d}\n====================\n".format(2255))
			f.seek(0x50d8,0)
			for i in range(2255):
				lin = f.readUint16()
				pad = (lin%2)
				if pad:
					lin+=pad
				string = f.read(lin).replace(b"\x00",b"").decode("utf-8")
				strings.write("[{0:04d}]\n{1}\n------------------------------\n".format(i,string))
			fileSave(strings.getdata().encode("utf-8"),"{0}{1:04d}_{2}/{3}.txt".format(folder,numTxt,self.name[:-4],self.name[:-4]))
		elif self.name == "mission.kst":
			f = self.data
			strings = Br(io.StringIO(""))
			strings.write("NOTE:\n------------------------------\nTOTAL_STRING:{0:04d}\n====================\n".format(635))
			f.seek(0x10b5a,0)
			for i in range(635):
				lin = f.readUint16()
				pad = (lin%2)
				if pad:
					lin+=pad
				string = f.read(lin).replace(b"\x00",b"").decode("utf-8")
				strings.write("[{0:04d}]\n{1}\n------------------------------\n".format(i,string))
			fileSave(strings.getdata().encode("utf-8"),"{0}{1:04d}_{2}/{3}.txt".format(folder,numTxt,self.name[:-4],self.name[:-4]))
		else:
			fileSave("NOT CONTAINING PLAINTEXT".encode("utf-8"),"{0}{1:04d}_{2}/{3}.txt".format(folder,numTxt,self.name[:-4],self.name[:-4]))
	def repack(self):
		folder = self.folder
		if self.name == "article.kst":
			from LISTFILE import artpoi
			f = self.data
			base = 0x39740
			f.seek(0x0C,0)
			total = f.readUint32()
			pointer = []
			newTxt = Br(open("{0}{1:04d}_{2}/{3}.txt".format(folder,numTxt,self.name[:-4],self.name[:-4]),"r"))
			note = newTxt.rt()
			totalstr = newTxt.readline()
			newTxt.readline()
			strings = Br(io.BytesIO())
			f.seek(base,0)
			for i in range(total-5):
				offset = strings.tell()+base
				pointer.append(offset)
				num= newTxt.readline()
				string = newTxt.rt().encode("utf-8")
				size = len(string)
				strings.writeUint16(size)
				term = size%2+1
				strings.write(string[:-1])
				strings.write(b"\x00"*term)
			pad = (16-(strings.tell() % 16))
			if pad:
				strings.write(b"\x00"*pad)
			f.seek(0x4a0)
			for i in range(total):
				f.read(12)
				f.writeUint32(pointer[artpoi[i]])
				f.read(32)
			return f.getBytes(0,base)+ strings.getdata()
		elif self.name == "article_ex.kst":
			from LISTFILE import artexpoi
			f = self.data
			base = 0x50d8
			f.seek(0x0C,0)
			total = f.readUint32()
			pointer = []
			newTxt = Br(open("{0}{1:04d}_{2}/{3}.txt".format(folder,numTxt,self.name[:-4],self.name[:-4]),"r"))
			note = newTxt.rt()
			totalstr = newTxt.readline()
			newTxt.readline()
			strings = Br(io.BytesIO())
			f.seek(base,0)
			for i in range(2255):
				offset = strings.tell()+base
				pointer.append(offset)
				num= newTxt.readline()
				string = newTxt.rt().encode("utf-8")
				size = len(string)
				strings.writeUint16(size)
				term = size%2+1
				strings.write(string[:-1])
				strings.write(b"\x00"*term)
			pad = (16-(strings.tell() % 16))
			if pad:
				strings.write(b"\x00"*pad)
			f.seek(0x4a0)
			for i in range(total):
				f.writeUint32(pointer[artexpoi[i]])
			return f.getBytes(0,base)+ strings.getdata()
		elif self.name == "mission.kst":
			from LISTFILE import mispoi
			f = self.data
			base = 0x10b5a
			pointer = []
			newTxt = Br(open("{0}{1:04d}_{2}/{3}.txt".format(folder,numTxt,self.name[:-4],self.name[:-4]),"r"))
			note = newTxt.rt()
			totalstr = newTxt.readline()
			newTxt.readline()
			strings = Br(io.BytesIO())
			f.seek(base,0)
			for i in range(635):
				offset = strings.tell()+base
				pointer.append(offset)
				num= newTxt.readline()
				string = newTxt.rt().encode("utf-8")
				size = len(string)
				strings.writeUint16(size)
				term = size%2+1
				strings.write(string[:-1])
				strings.write(b"\x00"*term)
			pad = (16-(strings.tell() % 16))
			if pad:
				pad+=6
				strings.write(b"\x00"*pad)
			f.seek(0x1124)
			k = 0
			for  i in range(394):
				f.read(148)
				f.writeUint32(pointer[mispoi[k]])
				k+=1
				f.writeUint32(pointer[mispoi[k]])
				k+=1
				f.writeUint32(pointer[mispoi[k]])
				k+=1
			return f.getBytes(0,base)+ strings.getdata()
		else:
			return self.data.getdata()
class Pres:
	def __init__(self,data,folder,name):
		self.data = Br(io.BytesIO(data))
		self.exfolder = folder
		self.name = os.path.basename(name)
		self.newname = name
		magic = self.data.read(8)
		unk = self.data.read(4)
		unk1 = self.data.read(4)
		self.tocSize = self.data.readUint32()
		dataOff = self.data.readUint32()
		dataSize = self.data.readUint32()
		null = self.data.read(4)
	def unpack(self):
		#print(self.name)
		res = self.data
		res.seek(0x30,0)
		grupOff = res.readUint32()
		grupItem = res.readUint32()
		grup = Br(io.BytesIO(res.getBytes(grupOff, (grupItem*32))))
		for numItem in range(grupItem):
			offsetFile = grup.readUint32()&0xffffff
			#print(hex(offsetFile))
			fileCsize = grup.readUint32()
			offName = grup.readUint32()
			element = grup.readUint32()
			res.seek(offName,0)
			null = grup.read(12)
			fileDsize = grup.readUint32()
			if offName:
				name = res.getUtf8(res.readUint32())
				ext = res.getUtf8(res.readUint32())
				fullname = name+"."+ext
				if ext == "conf":
					fullname+=".txt"
				print(fullname, hex(fileCsize),hex(fileDsize))
				data = blz((res.getBytes(offsetFile,fileCsize)), fileCsize,fileDsize)
				if ext == "tr2":
					tr2 = Tr2(data,self.exfolder+self.name[:-5]+ "/",fullname)
					tr2.unpack()
					
				elif ext == "conf":
					fileSave(data,self.exfolder+self.name[:-5]+ "/" +fullname)
				else:
					continue
					#fileSave(data,self.exfolder+self.name[:-5]+ "/" +fullname)
				
	def repack(self):
		print(self.name)
		res = self.data
		res.seek(0x30,0)
		grupOff = res.readUint32()
		grupItem = res.readUint32()
		grup = Br(io.BytesIO(res.getBytes(grupOff, (grupItem*32))))
		newGrup = Br(io.BytesIO(res.getBytes(grupOff, (grupItem*32))))
		newFiles = Br(io.BytesIO())
		for numItem in range(grupItem):
			offsetFile = grup.readUint32()&0xffffff
			fileCsize = grup.readUint32()
			offName = grup.readUint32()
			element = grup.readUint32()
			res.seek(offName,0)
			null = grup.read(12)
			fileDsize = grup.readUint32()
			if offName:
				name = res.getUtf8(res.readUint32())
				ext = res.getUtf8(res.readUint32())
				fullname = name+"."+ext
				if ext == "conf":
					fullname+=".txt"
				print(fullname, hex(fileCsize),hex(fileDsize))
				data = blz((res.getBytes(offsetFile,fileCsize)), fileCsize,fileDsize)
				if ext == "tr2":
					tr2 = Tr2(data,self.exfolder+self.name[:-5]+ "/",fullname)
					newFiledata = tr2.repack()
					newDecSize = len(newFiledata)
					newComFiledata = blz_com(newFiledata,newDecSize)
					newComSize = len(newComFiledata)
				elif fullname == "menu_font.conf.txt":
					newFiledata = open(self.exfolder+self.name[:-5]+ "/"+fullname, "rb").read()
					newDecSize = len(newFiledata)
					newComFiledata = blz_com(newFiledata,newDecSize)
					newComSize = len(newComFiledata)
				
				else:
					newFiledata = data # open(self.exfolder+self.name[:-5]+ "/"+fullname, "rb").read()
					newDecSize = len(newFiledata)
					idcom = res.getBytes(offsetFile,4)
					if idcom == b"blz2":
						newComFiledata = blz_com(newFiledata,newDecSize)
					else:
						newComFiledata = newFiledata
					newComSize = len(newComFiledata)
				newOff = (newFiles.tell()+self.tocSize)|0xc0000000
				newGrup.writeUint32(newOff)
				newGrup.writeUint32(newComSize)
				newGrup.read(20)
				newGrup.writeUint32(newDecSize)
				newFiles.write(newComFiledata)
				
				pad = 16 - (newComSize % 16 or 16)
				if pad:
					
					newFiles.write(b"\x00"*pad)
					
				
				
				
					
					
			else:
				newGrup.read(32)
		res.seek(grupOff,0)
		res.write(newGrup.getdata())
		fileSave(res.getBytes(0,self.tocSize)+ newFiles.getdata(), self.newname)
				

class Extractor:
	def __init__(self,nameIso, namePatch, nameSys,extractFolder):
		iso = Br(open(nameIso, "r+b"))
		patch = Br(open(namePatch, "r+b"))
		self.system = open(nameSys, "rb").read()
		self.folder = extractFolder
		self.nPatch = namePatch
		self.nameSys = nameSys
		basepkg = 0x1ff7b800
		basedata = 0x112ee000
		self.addbase ={0x50:basedata,0x40:basepkg,0x60:0,0:0}
		self.switchloc = {0x50:iso,0x40:iso, 0x60:patch}
	def extract(self):
		i = 0
		global numTxt
		numTxt=0
		system = Pres(self.system,self.folder,self.nameSys)
		system.unpack()
		for file in LISTFILE:
			name = file[0]
			print("{0:04d}_{1}".format(numTxt,name))
			offset = self.addbase[file[2]]+file[1]
			f = self.switchloc[file[2]]
			comSize,decSize= file[5],file[6]
			fileData =blz(f.getBytes(offset,comSize),comSize,decSize)
			if name[-3:] == "tr2":
				tr2 = Tr2(fileData,self.folder,name)
				tr2.unpack()
			elif name[-3:] == "kst":
				kst = Kst(fileData,self.folder,name)
				kst.unpack()
			numTxt+=1
	def insert(self):
		i = 0
		global numTxt
		numTxt=0	
		basePatch = 0x6b8b000
		exPatch = Br(io.BytesIO())
		system = Pres(self.system,self.folder,self.nameSys)
		system.repack()
		for file in LISTFILE:
			name = file[0]
			print("{0:04d}_{1}".format(numTxt,name))
			offset = self.addbase[file[2]]+file[1]
			f = self.switchloc[file[2]]
			comSize,decSize= file[5],file[6]
			fileData =blz(f.getBytes(offset,comSize),comSize,decSize)
			if name[-3:] == "tr2":
				tr2 = Tr2(fileData,self.folder,name)
				newFiledata = tr2.repack()
				newDecSize = len(newFiledata)
				newComFiledata = blz_com(newFiledata,newDecSize)
				newComSize = len(newComFiledata)
			else:
				kst = Kst(fileData,self.folder,name)
				newFiledata = kst.repack()
				newDecSize = len(newFiledata)
				newComFiledata = blz_com(newFiledata,newDecSize)
				newComSize = len(newComFiledata)
			poin = self.switchloc[file[4]]
			poin.seek(self.addbase[file[4]]+file[3],0)
			newOffset = ((exPatch.tell()+basePatch)//0x800)|0x60000000
			exPatch.write(newComFiledata)
			pad = 0x800 - (newComSize % 0x800 or 0x800)
			if pad:
				exPatch.write(b"\x00"*pad)
			poin.writeUint32(newOffset)
			poin.writeUint32(newComSize)
			poin.read(4)
			poin.read(16)
			poin.writeUint32(newDecSize)
			numTxt+=1
		baseGim= exPatch.getsize()+basePatch
		patchGim = InjectTex(baseGim)
		newPatchSize = baseGim+ len(patchGim)
		iso = self.switchloc[0x50]
		iso.seek(0x4ba24,0)
		iso.writeUint16(newPatchSize>>16)
		iso.read(10)
		iso.writeUint16(newPatchSize&0xffff)
	
		fileSave(self.switchloc[0x60].getBytes(0,basePatch)+exPatch.getdata()+patchGim,self.nPatch)
		
class Main:
	global numTxt
	cfg = open("INJECTOR.cfg","r")
	nIso = cfg.readline()[:-1].split("=")[-1]
	nPatch = cfg.readline()[:-1].split("=")[-1]
	nSys = cfg.readline()[:-1].split("=")[-1]
	exFolder =  cfg.readline()[:-1].split("=")[-1]
	mode = cfg.readline()[:-1].split("=")[-1]
	ex = Extractor(nIso,nPatch,nSys,exFolder)
	if mode == "-X":
		ex.extract()
		
	elif mode == "-I":
		ex.insert()
		
	else:
		sys.exit()
	
		
			
	
if __name__ == "__main__":
	Main()