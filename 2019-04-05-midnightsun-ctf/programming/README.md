# MidnightSun CTF - Polyshell (programming)

Challenge description:
> You might be cool, but are you 5 popped shells cool?
> > Service: nc polyshell-01.play.midnightsunctf.se 30000

After connecting we're welcomed with the message similar to the following one:
```txt

Welcome to the polyglot challenge!
Your task is to create a shellcode that can run on the following architectures:
x86
x86-64
ARM
ARM64
MIPS-LE

The shellcode must run within 1 second(s) and may run for at most 100000 cycles.
The code must perform a syscall on each platform according to the following paramters:
Syscall number: 102
Argument 1: 19701
Argument 2: A pointer to the string "natural"

You submit your code as a hex encoded string of max 4096 characters (2048 bytes)

Your shellcode:
```
Seems like a rather tough challenge.

Also, the syscall number and arguments differ between connections.

After a bit of googling one of our teammates found
[this code](https://github.com/ixty/xarch_shellcode/blob/master/stage0/poc.asm).
This code branches to different labels using instructions that are interpreted
as jump instructions on some architectures and are still valid instructions on
other architectures.
We only needed to add MIPS-LE to this bag.

MIPS-LE instructions are 4 bytes wide, just like ARM's and ARM64's.

The first 4 bytes:
```nasm
    db 0xeb, (_x86 - $ - 2), 0x00, 0x32
```
are interpreted on MIPS-LE as
```mips
    andi zero, s0, 0x12eb.
```
Almost good, but not yet, because register `zero` isn't
writable. I only had to change the 3rd byte:
```nasm
    db 0xeb, (_x86 - $ - 2), 0x12, 0x32
```
After this change it's interpreted on MIPS-LE as
```mips
    andi    s2, s0, 0x12eb
```
and still won't break on ARM and ARM64.

The next 4 bytes, which are interpreted as jump on ARM, aren't so easily
fixable, so I've decided to check how MIPS-LE's jump instruction are interpreted
on ARM and ARM64.

MIPS-LE has jump and branch instructions. Jump instructions are absolute so we
can't really use them reliably because we don't know where our shellcode resides
in memory. Branch instructions are relative. I've decided to use
```mips
    beq     s0, s0, _mips
```
Most times it's true that `s0 == s0`, so this will always jump to `_mips` label.
Bytes of this instruction are interpreted as
```arm
    andscc  r1, r2, #0xb000000e
```
and
```aarch64
    orr     w11, w23, #0x7c000
```
on ARM and ARM64 respectively, so we're safe.

MIPS will always execute pipelined instruction right after the jump, so we need
some valid MIPS-LE (and ARM and ARM64) instruction right after this jump. I've
just copied the very first one.

I've used pwnlib's shellcraft module to generate syscall payloads for all
architectures. (See [get\_nasm\_syscall\_code](solve.py#L38-L43))

See [`poc.asm`](poc.asm) for the full polyglot shellcode.


## Starting the solution
```sh
    python2 solve.py
```
(you need to have pwntools installed)
