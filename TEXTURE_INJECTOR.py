from NF import *
import glob,png,zlib
from PIL import Image
def blz_com(data, dsize):
    f = Br(io.BytesIO(data))

    def compress_chunk(size):
        deflate_compress = zlib.compressobj(9, zlib.DEFLATED, -15)
        data = deflate_compress.compress(f.read(size)) + deflate_compress.flush()
        chunksize = len(data).to_bytes(2, byteorder='little', signed=False)
        data = chunksize + data
        return data

    # ---------------------
    deflate_compress = zlib.compressobj(9, zlib.DEFLATED, -15)
    tail_size = dsize % 0xffff
    number_part = dsize // 0xffff
    # ---------------------
    if dsize < 0xffff:
        compressed = None
        compressed = deflate_compress.compress(f.read()) + deflate_compress.flush()
        chunksize = len(compressed).to_bytes(2, byteorder='little', signed=False)
        compressed = b"blz2" + chunksize + compressed
        return compressed
    # ---------------------
    else:
        compressed = b""
        i = 0
        head = compress_chunk(tail_size)
        compressed = compressed + head
        while i < number_part - 1:
            chunk = compress_chunk(0xffff)
            compressed = compressed + chunk
            i += 1
        last_chunk = compress_chunk(0xffff)
        compressed = b'blz2' + last_chunk + compressed
        return compressed





class Gim:
    def __init__(self,data):
        self.data = Br(io.BytesIO(data))
        self.tmp = Br(io.BytesIO(data))
        self.data.seek(0x34, 0)
        self.palpos = self.data.readUint32() + 0x80
        self.data.seek(0x44, 0)
        self.bpp = self.data.readUint16()
        self.data.read(2)
        self.w = self.data.readUint16()
        self.h = self.data.readUint16()
        self.paddding = self.data.readUint8()
    def swizz(self,data,w,h,bit):
        f = Br(io.BytesIO(data))
        tmp = Br(io.BytesIO())
        blockH = h//8
        blockW = w//16
        for xx in range(blockH):
            for yy in range(blockW):
                for zz in range(8):
                    position = (((xx*w)*8) +(yy*16*bit)+(zz*w))
                    tmp.write(f.getBytes(position, 16*bit))
        return tmp.getdata()
    def unswizz(self,data,w,h,bit):
        bin = io.BytesIO(data)
        s = []
        for xx in range(h // 8):
                list = []
                for y in range(8):
                    list.append([])
                for x in range(w // (16*bit)):
                          for z in range(8):
                            list[z].extend(bin.read(16*bit))
                for zz in list:
                    s.append(zz)
        return s
    def bpp4(self,data):
        i =0
        z = len(data)
        tmp = bytearray(data)
        new = bytearray()
        while i < z:
                new.append((tmp[i] ) |((tmp[i+1]) << 4))
                i+=2
        return bytes(new)
    def toBin(self,name):
        self.pngName = name
        if self.bpp == 0:
            return  self.Rgba5650()
        elif self.bpp == 1:
            return  self.Rgba5551()
        elif self.bpp == 2:
            return  self.Rgba4444()
        elif self.bpp == 3:
            return  self.Rgba8888()
        elif self.bpp == 4:
            return  self.Index4()
        elif self.bpp == 5:
            return  self.Index8()
    def Rgba5650(self):
        pass
    def Rgba5551(self):
        pass
    def Rgba4444(self):
        pass
    def Rgba8888(self):
        r = png.Reader(open(self.pngName, 'rb'))
        p = r.read()
        height = p[1]
        width = p[0]
        try:
            pal = p[3]["palette"]
            print("mode rgba, Quantize dulu")
            img = Image.open(self.pngName).convert("RGBA")
            img.save(self.pngName)
        except:
            r = png.Reader(open(self.pngName, 'rb'))
            p = r.read()
            height = p[1]
            width = p[0]
        l = list(p[2])
        tmpTile = Br(io.BytesIO())
        for x in range(height):
            d = bytes(l[x])
            tmpTile.write(d)
            pad = self.w %4
            if pad:
                tmpTile.wpad(self.paddding)
        # tmpGim = self.data.getdata()
        self.tmp.seek(0x80, 0)
        self.tmp.write(tmpTile.getdata())
        sizeGim = self.data.tell()
        return self.tmp.getdata()
    def Index4(self):
        r = png.Reader(open(self.pngName, 'rb'))
        p = r.read()
        height = p[1]
        width = p[0]
        try:
            pal = p[3]["palette"]
        except:
            print("mode rgba, Quantize dulu")
            img = Image.open(self.pngName).quantize(16, method=2)
            img.save(self.pngName)
            r = png.Reader(open(self.pngName, 'rb'))
            p = r.read()
            height = p[1]
            width = p[0]
        l = list(p[2])
        pal = p[3]["palette"]
        bPal = Br(io.BytesIO())
        tmpTile = Br(io.BytesIO())
        for j in range(16):
            bPal.write(bytes(pal[j]))
        for x in range(height):
            d = bytes(l[x])
            tmpTile.write(d)
            pad = self.w % 4
            if pad:
                tmpTile.wpad(self.paddding)
        # tmpGim = self.data.getdata()
        tmpTile = Br(io.BytesIO(self.bpp4(tmpTile.getdata())))
        self.tmp.seek(0x80, 0)
        self.tmp.write(tmpTile.getdata())
        self.tmp.seek(self.palpos, 0)
        self.tmp.write(bPal.getdata())
        return self.tmp.getdata()
    def Index8(self):
        r = png.Reader(open(self.pngName, 'rb'))
        p = r.read()
        height = p[1]
        width = p[0]
        try:
            pal = p[3]["palette"]
        except:
            print("mode rgba, Quantize dulu")
            img = Image.open(self.pngName).quantize(256, method=2)
            img.save(self.pngName)
            r = png.Reader(open(self.pngName, 'rb'))
            p = r.read()
            height = p[1]
            width = p[0]
        l = list(p[2])
        pal = p[3]["palette"]
        bPal = Br(io.BytesIO())
        tmpTile = Br(io.BytesIO())
        for j in range(256):
            bPal.write(bytes(pal[j]))
        for x in range(height):
            d = bytes(l[x])
            tmpTile.write(d)
            pad = self.w % 4
            if pad:
                tmpTile.wpad(self.paddding)
        #tmpGim = self.data.getdata()
        self.tmp.seek(0x80,0)
        self.tmp.write(tmpTile.getdata())
        self.tmp.seek(self.palpos,0)
        self.tmp.write(bPal.getdata())
        sizeGim = self.data.tell()
        return self.tmp.getdata()


class Main:
    def makegGimPatch(basepatch):
        path = "EDITED_PNG/*/"+"*.png"
        lgim = open("LGIM.py","w")
        pngNames  = glob.glob(path)
        lgim.write("lgim ={\n")
        patchGim = Br(io.BytesIO())
        for pngName in pngNames:
            gimName = "EDITED_GIM/"+pngName[11:-3].replace("\\","/")+"gim"
            print(gimName)
            k = gimName.split("/")
            crc = k[-1][:8]
            dataGim = open(gimName,"rb").read()
            gim = Gim(dataGim)
            newGim = gim.toBin(pngName)
            #fileSave(newGim,pngName+"xxx")#untuk debug
            dsize = len(newGim)
            comGim = blz_com(newGim,dsize)
            csize = len(comGim)
            #print("INSERTING>>> "+gimName)
            offsetfile = patchGim.tell()+basepatch
            patchGim.write(comGim)
            patchGim.wpad(0x800)
            lgim.write("\'{0}\':[0x{1:08X},0x{2:08X},0x{3:08X}],\n".format(k[-1].upper(), offsetfile // 0x800, csize, dsize))
        lgim.write("}")
        lgim.close()
        from LGIM import lgim
        list = open("LISTGIM2.dat", "r")
        switchBase = {"pkg":0x1ff7b800,"data":0x112ee000,"patch":0,}
        switchLoc = {"pkg":iso,"data":iso,"patch":patch}
        for line in list:
            s = line[:-1].split(",")
            poinName = s[0][9:]
            poinOff = int(s[1][8:],16)#+switchBase[poinName]
            poin =switchLoc[poinName]
            fullName = s[2].upper()
            
            poin.seek(poinOff,0)
            try:
                newDataGim = lgim[fullName]
                newOffset = newDataGim[0]
                print(hex(newOffset),fullName)
                newCsize = newDataGim[1]
                newDsize = newDataGim[2]
                poin.writeUint32(newOffset | 0x60000000)
                poin.writeUint32(newCsize)
                poin.read(20)
                poin.writeUint32(newDsize)
                print("injected",fullName)
                
            except:
                continue
        newPatchSize = basepatch +patchGim.getsize()
        iso.seek(0x4ba24, 0)
        iso.writeUint16(newPatchSize >> 16)
        iso.read(10)
        iso.writeUint16(newPatchSize & 0xffff)
        return patchGim.getdata()
        #fileSave(patch.getBytes(0,basepatch) + patchGim.getdata(),patchName )


#if __name__ == "__main__":
def InjectTex(basepatch):
    global iso,patch,debug,patchName,tt
    cfg = open("INJECTOR.cfg","r")
    isoName = cfg.readline()[:-1].split("=")[-1]
    patchName = cfg.readline()[:-1].split("=")[-1]
    debug = False
    iso =Br(open(isoName,"r+b"))
    patch = Br(open(patchName,"r+b"))
    return Main.makegGimPatch(basepatch)
    
    
    