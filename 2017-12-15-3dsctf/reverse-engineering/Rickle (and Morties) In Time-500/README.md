Rickle (and Morties) in Time
===
**Category:** Reverse Engineering, **Points:** 500, **Solves:** 14, First solve

Morty ruined everything again and now there's more than one point on the screen. Help Rick fix the time.

### Write-up

We are given 5 ELF executables - `rick` and 4 `morties`. Let's run them:

    $ ./rick 
    Gzzes Morty, where we are?
    $ ./morty-1
    Where am I?
    $ ./morty-2
    Where am I?
    $ ./morty-3
    Where am I?
    $ ./morty-4
    Where am I?

As description of this task says, we have to help Rick fix the time, because everyone is lost... Then let's see what's inside the binaries, luckily they are not stripped so analysis is easier.

#### Rick

    rickLocation = getCurrentDir();
    c = 0;
    if ( strcmp(rickLocation, "137") )
    {
        fwrite("Gzzes Morty, where we are?\n", 1uLL, 0x1BuLL, stderr);
        exit(1);
    }
    if ( access(device /*../neckless-device*/, 0) == -1 )
    {
        fwrite("Where did you put the neckless?!?\n", 1uLL, 0x22uLL, stderr);
        exit(1);
    }
    if ( access(safePlace, 0) == -1 )
    {
        fwrite("Where I suppose to send you?\n", 1uLL, 0x1DuLL, stderr);
        exit(1);
    }
    fD = fopen(device, "a+");
    for ( i = fgets(current, 32, fD); i; i = fgets(current, 32, fD) )
        ++c;
    fclose(fD);
    if ( c )
    {
        puts("Don't play with parallel universes, Morty!");
        exit(1);
    }
    puts("OK, Morty let's sync...");
    syncronize();
    puts("Jesus, Morty! The gun was in reverse mode...");

There are few requirements before they all `synchronize`. `Rick` must be started from `137` folder, there must be files `../neckless-device` and `../earth-137`. File `neckless-device` must be empty, otherwise message `"Don't play with parallel universes, Morty!"` is shown, now after we created those files, moved binary to folder, we see `"OK, Morty let's sync..."` message and in file `neckless-device` string appeared:

    rick-34749-0

The first number is `pid` and second one is some internal id. In function `keepSyncronized` rick is waiting for `morty` process with pid equals: **rick's pid + 1**.

#### Morties

`Morties` are similar to `rick` - they want to be in folders `137-1`, `137-2`, `137-3`, `137-4` and also requires those two files, but `neckless-device` doesn't have to be empty.

#### Running it all together

Let's put everything in correct folder, create file `neckless-device` and `earth-137`, run `rick`, `morty1`, `morty2`, `morty3`, `morty4`, each process added its line to `neckless device`:

    rick-34863-0
    morty-1-34864-0
    morty-2-34866-0
    morty-3-34869-0
    morty-4-36103-0

But nothing more happens. That's because all process requires to have specific pid values - `rick's pid`, `rick's pid + 1`, `rick's pid + 2`, `rick's pid + 3`, `rick's pid + 4`. We could try to be really fast so that no other process start between next process startup... or we can modify binary so that instead of using `getpid` function, constant number is returned. Or we can use linux [LD_PRELOAD mechanism](https://stackoverflow.com/questions/426230/what-is-the-ld-preload-trick) to override `getpid` function used by executables. That's very convenient solution and I will use it here.

Let's create extremely simple shared library, which in `getpid` function returns value of environment variable:

    #include <unistd.h>
    #include <stdlib.h>

    pid_t getpid() {
            return atoi(getenv("FAKEPID"));
    }

Compile it:

    gcc -fPIC -shared -o fakepid.so fakepid.c

and now run binaries the following way:

    $ export FAKEPID="0" && LD_PRELOAD=../fakepid.so ./rick
    $ export FAKEPID="1" && LD_PRELOAD=../fakepid.so ./morty-1
    $ export FAKEPID="2" && LD_PRELOAD=../fakepid.so ./morty-2
    $ export FAKEPID="3" && LD_PRELOAD=../fakepid.so ./morty-3
    $ export FAKEPID="4" && LD_PRELOAD=../fakepid.so ./morty-4

This time when thoses process call `getpid` function, my overriden function will be called insted of the one from libc. Now all processes are synchronized!

    $ cat neckless-device
    rick-0-0
    morty-1-1-0
    morty-2-2-0
    morty-3-3-0
    morty-4-4-0
    rick-0-1
    morty-1-1-1
    morty-2-2-1
    morty-3-3-1
    morty-4-4-1
    rick-0-2
    morty-1-1-2
    morty-2-2-2
    morty-3-3-2
    morty-4-4-2
    rick-0-3
    morty-1-1-3
    morty-2-2-3
    ...

After few seconds they all end and rick says:

    Jesus, Morty! The gun was in reverse mode...

The file `earth-137` contains text which looks like base64 encoded, however decoding doesn't give any reasonable result:

    $ base64 --decode < earth-137 > decoded
    $ file decoded 
    decoded: data

It turned out the clue is in last `rick` message:

> The gun was in **reverse mode**...

We need to reverse `earth-137` first!

    $ rev earth-137 | base64 --decode > decoded
    $ file decoded 
    decoded: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=731e9f329f5597f85ad1a6e4b59301c7c4395e6c, not stripped

And the result is another executable file... Let it be flag:

    $ ./decoded 
    3DS{Wubba-luBBa-dUb-Dub}

Flag found!


###### Bartek aka bandysc 
