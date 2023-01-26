import pythonmemorymodule, sys
from ctypes import *
from struct import pack, calcsize
import binascii
import cmd
RUNCOFFCALLBACK = WINFUNCTYPE(None, c_char_p, c_int)

@RUNCOFFCALLBACK
def pycallback(outstr, len_outstr):
    print(outstr)

RUNCOFFPROC = WINFUNCTYPE(c_int, c_char_p, c_int, RUNCOFFCALLBACK)


def bofrun(bofpath, args):
    with open("COFFLoader/COFFLoader.x64.dll", 'rb') as f:
        coffl = f.read() # DYNAMIC BUFFER POG

    bof_path = sys.argv[1]
    with open(bofpath, 'rb') as f:
        boffile = f.read() # DYNAMIC BUFFER POG


    dll = pythonmemorymodule.MemoryModule(data=coffl, debug=False)
    
    runcoff = RUNCOFFPROC(dll.get_proc_addr_raw("LoadAndRun"))

    bofdata = BeaconPack()
    bofdata.addstr("go")
    bofdata.addstr(boffile)
    bofdata.addstr(args)
    
    bofdata_buf = bofdata.getbuffer()
    
    runcoff(bofdata_buf, len(bofdata_buf), pycallback)


# stolen from COFFLoader


class BeaconPack:
    def __init__(self):
        self.buffer = b''
        self.size = 0

    def getbuffer(self):
        return pack("<L", self.size) + self.buffer

    def addshort(self, short):
        self.buffer += pack("<h", short)
        self.size += 2

    def addint(self, dint):
        self.buffer += pack("<i", dint)
        self.size += 4

    def addstr(self, s):
        if isinstance(s, str):
            s = s.encode("utf-8")
        fmt = "<L{}s".format(len(s) + 1)
        self.buffer += pack(fmt, len(s)+1, s)
        self.size += calcsize(fmt)

    def addWstr(self, s):
        if isinstance(s, str):
            s = s.encode("utf-16_le")
        fmt = "<L{}s".format(len(s) + 2)
        self.buffer += pack(fmt, len(s)+2, s)
        self.size += calcsize(fmt)

class MainLoop(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.BeaconPack = BeaconPack()
        self.intro = "Beacon Argument Generator/In-memory Runner\nbeacon file:"+sys.argv[1]
        self.prompt = "Beacon>"
    
    def do_addWString(self, text):
        '''addWString String here
        Append the wide string to the text.
        '''
        self.BeaconPack.addWstr(text)

    def do_run(self, text):
        '''run
        Run the bof with the specified arguments
        '''
        outbuffer = self.BeaconPack.getbuffer()
        bofrun(sys.argv[1], outbuffer)

    
    def do_addString(self, text):
        '''addString string here
        Append the utf-8 string here.
        '''
        self.BeaconPack.addstr(text)
    
    def do_generate(self, text):
        '''generate
        Generate the buffer for the BOF arguments
        '''
        outbuffer = self.BeaconPack.getbuffer()
        print(binascii.hexlify(outbuffer))
    
    def do_addint(self, text):
        '''addint integer
        Add an int32_t to the buffer
        '''
        try:
            converted = int(text)
            self.BeaconPack.addint(converted)
        except:
            print("Failed to convert to int\n");

    def do_addshort(self, text):
        '''addshort integer
        Add an uint16_t to the buffer
        '''
        try:
            converted = int(text)
            self.BeaconPack.addshort(converted)
        except:
            print("Failed to convert to short\n");
    
    def do_reset(self, text):
        '''reset
        Reset the buffer here.
        '''
        self.BeaconPack.buffer = b''
        self.BeaconPack.size = 0
    
    def do_exit(self, text):
        '''exit
        Exit the console
        '''
        return True

if __name__ == "__main__":
    cmdloop = MainLoop()
    cmdloop.cmdloop()

