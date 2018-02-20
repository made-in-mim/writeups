Flea Attack
===

**Category:** pwn, **Points:** 200, **Solves:** 41

```
nc problem.harekaze.com 20175

file: flea_attack
```

## Writeup

Let's run the binary and check what is actually does:

```
$ ./flea_attack.elf
Some comment this note:note
1. Add name
2. Delete name
3. Exit
> 1
Size: 10
Name: name
Done!
Name: name

Addr: 173a250
1. Add name
2. Delete name
3. Exit
> 2
Addr: 173a250
Done!
1. Add name
2. Delete name
3. Exit
> Invalid
1. Add name
2. Delete name
3. Exit
> 3
Bye.
```

Now, let's take a look at the code. The binary contains debugging symbols,
so it is even easier to analyze:

```c
int main()
{
  struct _IO_FILE *v3; // rdi@1
  int v4; // [sp+38h] [bp-8h]@2

  setvbuf(stdin, 0LL, 2, 0LL);
  setvbuf(stdout, 0LL, 2, 0LL);
  v3 = stderr;
  setvbuf(stderr, 0LL, 2, 0LL);
  open_flag(v3, 0LL);
  printf("Some comment this note:");
  gets_comment();
  while ( 1 )
  {
    show_menu();
    printf("> ");
    v4 = gets_int();
    switch ( v4 )
    {
      case 1:
        add_name();
        break;
      case 2:
        del_name();
        break;
      case 3:
        puts("Bye.");
        exit(0);
        break;
      default:
        puts("Invalid");
        break;
    }
  }
}
```

There is an interesting function called `open_flag`:

```c
char *open_flag()
{
  FILE *stream; // [sp+18h] [bp-8h]@1

  stream = fopen("/home/flea_attack/flag", "r");
  if ( !stream )
  {
    puts("ERROR: Open Error");
    exit(1);
  }
  return fgets((char *)&flag, 48, stream);
}
```

It simply loads the flag to the memory. Exactly saying, to some global variable:
```
$ readelf --syms flea_attack.elf
... snip ...
36: 0000000000204000   128 OBJECT  GLOBAL DEFAULT   25 comment
... snip ...
40: 0000000000204080    48 OBJECT  GLOBAL DEFAULT   25 flag
```

After reading more code, we can see no sign of later usage of the flag. So, we
need to leak it somehow. Let's take a look at the `add_name`:

```c
int add_name()
{
  int v0; // ST2C_4@1
  void *buf; // ST20_8@1

  printf("Size: ");
  v0 = gets_int();
  buf = malloc(v0);
  printf("Name: ");
  read(0, buf, v0);
  puts("Done!");
  printf("Name: %s\n", buf);
  return printf("Addr: %llx\n", buf);
}
```

Do you see problem here? We malloc exactly `v0` bytes, then we read exactly `v0`
bytes. But `read` doesn't append null byte. And then - we `printf` that buffer.
Which means that we could possibly leak some memory that lies beyond our
buffer... Wait, why does it work during normal usage? Heap is being zeroed,
so it had null byte after our buffer.

So, how about convincing `malloc` to return address pointing to some memory
in front of our flag? That sounds like [fastbin dup attack](https://github.com/shellphish/how2heap/blob/master/fastbin_dup_into_stack.c).
So, what do we need?
* ability to `malloc` some data - *check*.
* ability to `free` some data - `del_name` does exactly it - *check*.
* control some memory right before the memory we want to leak - remember
`comment` global variable in the listing before? - *check*.

So, what we now need to do, is just following the steps from link above.

Exploit code can be found [in the same directory](solve.py) as this document.
Eventually, after running the script, we can get the flag: `HarekazeCTF{5m41l_smal1_f1ea_c0n7rol_7h3_w0rld}`.

###### By [mrowqa](https://github.com/Mrowqa) <artur.jamro@gmail.com>
