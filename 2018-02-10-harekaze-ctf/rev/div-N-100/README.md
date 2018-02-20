div N
===

**Category:** Rev, **Points:** 100, **Solves:** 90

```
$ cat foo.c
long long div(long long x) {
    return x / N;
}
$ gcc -DN=$N -c -O2 foo.c
$ objdump -d foo.o

foo.o:     file format elf64-x86-64


Disassembly of section .text:

0000000000000000
:
   0:	48 89 f8             	mov    %rdi,%rax
   3:	48 ba 01 0d 1a 82 9a 	movabs $0x49ea309a821a0d01,%rdx
   a:	30 ea 49
   d:	48 c1 ff 3f          	sar    $0x3f,%rdi
  11:	48 f7 ea             	imul   %rdx
  14:	48 c1 fa 30          	sar    $0x30,%rdx
  18:	48 89 d0             	mov    %rdx,%rax
  1b:	48 29 f8             	sub    %rdi,%rax
  1e:	c3                   	retq   
$ echo “HarekazeCTF{$N}” > /dev/null
```

## Writeup

My first attempt was to use [z3](https://github.com/Z3Prover/z3), but z3 was
unable to find the N. Another approach was to be smart and [try to analyze
the compiler optimization](https://reverseengineering.stackexchange.com/questions/1397/how-can-i-reverse-optimized-integer-division-modulo-by-constant-operations).

But, let's go another way. Notice one thing: `(N-1) / N = 0` and `N / N = 1`.
So we can just use simple binary search. How? We know that compiled program
is a 64 bit ELF and we are given the machine code encoded in hex. So let's just
load it to executable memory and run it:

```c++
#include <iostream>

int main() {
    char function[] = {"\x48\x89\xf8\x48\xba\x01\x0d\x1a\x82\x9a\x30\xea\x49\x48\xc1\xff\x3f\x48\xf7\xea\x48\xc1\xfa\x30\x48\x89\xd0\x48\x29\xf8\xc3"};
    long long (*foo_ptr)(long long) = (long long (*)(long long)) function;

    long long a = 0;
    long long b = 0x7FFFFFFFFFFFFFFF;

    while (b - a > 1) {
        long long mid = a / 2 + b / 2; // more or less; avoiding overflow
        if (foo_ptr(mid) >= 1) {
            b = mid;
        }
        else {
            a = mid;
        }
    }
    std::cout << a << "\n" << b << "\n";
}
```

So, let's compile it and run it:
```
$ g++ -z execstack -o x x.cpp
$ ./x
974873638438445
974873638438446
```
Who does say that `-z execstack` is bad? :P And, BTW, you don't want to compile
this code with any optimizations, since we are doing stuff we theoretically
shouldn't do and compiler assumes that we are reasonable programmers :)

So, finally, the flag is `HarekazeCTF{974873638438446}`.

###### By [mrowqa](https://github.com/Mrowqa) <artur.jamro@gmail.com>
