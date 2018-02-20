Ransomware
===
**Category:** Reverse Engineering, **Points:** 500, **Solves:** 48

> WARNING! DON'T EXECUTE THIS SAMPLE IN YOUR OWN PERSONAL MACHINE!!!

### Write-up

Safety first, so I have listened to authors and run the given windows portable executable in virtual machine. We are greeted by message:

    @@@@@@@@@@    @@@@@@    @@@@@@@   @@@@@@   @@@  @@@
    @@@@@@@@@@@  @@@@@@@@  @@@@@@@@  @@@@@@@@  @@@  @@@
    @@! @@! @@!  @@!  @@@  !@@       @@!  @@@  @@!  @@@
    !@! !@! !@!  !@!  @!@  !@!       !@!  @!@  !@!  @!@
    @!! !!@ @!@  @!@  !@!  !@!       @!@  !@!  @!@!@!@!
    !@!   ! !@!  !@!  !!!  !!!       !@!  !!!  !!!@!!!!
    !!:     !!:  !!:  !!!  :!!       !!:  !!!  !!:  !!!
    :!:     :!:  :!:  !:!  :!:       :!:  !:!  :!:  !:!
    :::     ::   ::::: ::   ::: :::  ::::: ::  ::   :::
    :      :     : :  :    :: :: :   : :  :    :   : :
    ---------------------------------------------------
    -====<(     mocoh ransomware decrypter!     )>====-
    ---------------------------------------------------
    ATTENTION!! do not try to decrypt if you did not
    purchase our product. A wrong attempt can cause
    irreversible damage... Be responsible!
    Doubts, criticisms and suggestions are important
    to improve our service.  Thank you! (SWaNk)
    ---------------------------------------------------
    Enter the purchased key:

The flag is encrypted so what worse can happen?

    Enter the purchased key: abcd
    Do you have backup right? Otherwise you are fucked...

And after few seconds Windows shuts down (and sadly I didn't guessed password).

Before we start analysis let's disarm the executable, so that it will not turn off the computer even if we put wrong password. Take a look at functions inside binary

![](assets/functions.png)

Luckily there is no magic to shut down the computer - it simply calls function `ExitWindowsEx`, which calls imported WinAPI function:

    .text:004008DE ExitWindowsEx   proc near
    .text:004008DE                 jmp     __imp_ExitWindowsEx
    .text:004008DE ExitWindowsEx   endp

PE loader fills memory under address `__imp_ExitWindowsEx` by actual address of Windows function. Let's just replace it with `NOPs`:

    .text:004008DE ExitWindowsEx:
    .text:004008DE                 nop
    .text:004008DF                 nop
    .text:004008E0                 nop
    .text:004008E1                 nop
    .text:004008E2                 nop
    .text:004008E3                 nop
    .text:004008E4 ExitProcess:

Quick test - same wrong password and now at least our unsave work is safe. IDA comes with really good decompiler, but this task shows that we shouldn't trust it even in simple programs:

    void sub_40023B()
    {
        char _0;
        sub_400798();
        console_print("\r\n");
        console_print("  @@@@@@@@@@    @@@@@@    @@@@@@@   @@@@@@   @@@  @@@");
        console_print("\r\n");
        console_print("  @@@@@@@@@@@  @@@@@@@@  @@@@@@@@  @@@@@@@@  @@@  @@@");
        console_print("\r\n");
        console_print("  @@! @@! @@!  @@!  @@@  !@@       @@!  @@@  @@!  @@@");
        console_print("\r\n");
        console_print("  !@! !@! !@!  !@!  @!@  !@!       !@!  @!@  !@!  @!@");
        console_print("\r\n");
        console_print("  @!! !!@ @!@  @!@  !@!  !@!       @!@  !@!  @!@!@!@!");
        console_print("\r\n");
        console_print("  !@!   ! !@!  !@!  !!!  !!!       !@!  !!!  !!!@!!!!");
        console_print("\r\n");
        console_print("  !!:     !!:  !!:  !!!  :!!       !!:  !!!  !!:  !!!");
        console_print("\r\n");
        console_print("  :!:     :!:  :!:  !:!  :!:       :!:  !:!  :!:  !:!");
        console_print("\r\n");
        console_print("  :::     ::   ::::: ::   ::: :::  ::::: ::  ::   :::");
        console_print("\r\n");
        console_print("   :      :     : :  :    :: :: :   : :  :    :   : :");
        console_print("\r\n");
        console_print("  ---------------------------------------------------");
        console_print("\r\n");
        console_print("  -====<(     mocoh ransomware decrypter!     )>====-");
        console_print("\r\n");
        console_print("  ---------------------------------------------------");
        console_print("\r\n");
        console_print("  ATTENTION!! do not try to decrypt if you did not   ");
        console_print("\r\n");
        console_print("  purchase our product. A wrong attempt can cause    ");
        console_print("\r\n");
        console_print("  irreversible damage... Be responsible!             ");
        console_print("\r\n");
        console_print("  Doubts, criticisms and suggestions are important   ");
        console_print("\r\n");
        console_print("  to improve our service.  Thank you! (SWaNk)        ");
        console_print("\r\n");
        console_print("  ---------------------------------------------------");
        console_print("\r\n");
        console_print("  Enter the purchased key: ");
        console_read(&password, 8);
        console_print("\r\n");
        console_print("  Do you have backup right? Otherwise you are fucked...");
        console_print("\r\n");
        console_print("\r\n");
        Sleep(1500);
        RtlAdjustPrivilege(19, 1, 0, &_0);
        return ExitWindowsEx(2, 10);
    }

It looks like no matter what password we type, it always shut down computer... but if we look at assembly... it turns out 

        .text:004003D0                 push    8
        .text:004003D2                 push    offset password
        .text:004003D7                 call    console_read
    --> .text:004003DC                 cmp     password, '52'
        .text:004003E5                 jnz     short invalid_1
        .text:004003E7                 mov     al, byte_4009BA
        .text:004003EC                 mov     ecx, 9
        .text:004003F1                 dec     ecx
        .text:004003F2                 lea     edx, dword_400984
        .text:004003F8                 call    sub_4005D0
        .text:004003FD                 push    offset dword_400984
        .text:00400402                 call    console_print
        .text:00400407                 jmp     short continue_check
        .text:00400409 ; ---------------------------------------------------------------
        .text:00400409
        .text:00400409 invalid_1:
        .text:00400409                 push    offset asc_400E74 ; "\r\n"
        .text:0040040E                 call    console_print
        .text:00400413                 push    offset aDoYouHaveBacku ; "  Do you have backup right? Otherwise y"...
        .text:00400418                 call    console_print
        .text:0040041D                 push    offset asc_400EB0 ; "\r\n"
        .text:00400422                 call    console_print
        .text:00400427                 push    offset asc_400EB4 ; "\r\n"
        .text:0040042C                 call    console_print
        .text:00400431                 jmp     exit_procedure
        .text:00400436 ; --------------------------------------------------
        .text:00400436
        .text:00400436 continue_check:
    --> .text:00400436                 cmp     password_offset_2, '30'
        .text:0040043F                 jnz     short invalid_2
        .text:00400441                 mov     al, byte_4009BB
        .text:00400446                 mov     ecx, 9
        .text:0040044B                 dec     ecx
        .text:0040044C                 lea     edx, byte_40098D
        .text:00400452                 call    sub_4005D0
        .text:00400457                 push    offset byte_40098D
        .text:0040045C                 call    console_print
        .text:00400461                 jmp     short continue_check_2
        .text:00400463 ; ---------------------------------------------------
        .text:00400463
        .text:00400463 invalid_2:
        .text:00400463                 push    offset asc_400EB8 ; "\r\n"
        .text:00400468                 call    console_print
        .text:0040046D                 push    offset aFuckItThen___ ; "  Fuck it then..."
        .text:00400472                 call    console_print
        .text:00400477                 push    offset asc_400ECE ; "\r\n"
        .text:0040047C                 call    console_print
        .text:00400481                 push    offset asc_400ED4 ; "\r\n"
        .text:00400486                 call    console_print
        .text:0040048B                 jmp     exit_procedure
        .text:00400490 ; ---------------------------------------------------
        .text:00400490
        .text:00400490 continue_check_2:
    --> .text:00400490                 cmp     password_offset_4, '91'
        .text:00400499                 jnz     short invalid_3
        .text:0040049B                 mov     al, byte_4009BC
        .text:004004A0                 mov     ecx, 9
        .text:004004A5                 dec     ecx
        .text:004004A6                 lea     edx, word_400996
        .text:004004AC                 call    sub_4005D0
        .text:004004B1                 push    offset word_400996
        .text:004004B6                 call    console_print
        .text:004004BB                 jmp     short continue_check_3
        .text:004004BD ; ---------------------------------------------------
        .text:004004BD
        .text:004004BD invalid_3:
        .text:004004BD                 push    offset asc_400ED8 ; "\r\n"
        .text:004004C2                 call    console_print
        .text:004004C7                 push    offset aGoFuckYourself ; "  Go fuck yourself."
        .text:004004CC                 call    console_print
        .text:004004D1                 push    offset asc_400EF0 ; "\r\n"
        .text:004004D6                 call    console_print
        .text:004004DB                 push    offset asc_400EF4 ; "\r\n"
        .text:004004E0                 call    console_print
        .text:004004E5                 jmp     exit_procedure
        .text:004004EA ; ---------------------------------------------
        .text:004004EA
        .text:004004EA continue_check_3:
    --> .text:004004EA                 cmp     password_offset_6, '97'
        .text:004004F3                 jnz     short invalid_4
        .text:004004F5                 mov     al, byte_4009BD
        .text:004004FA                 mov     ecx, 0Ah
        .text:004004FF                 dec     ecx
        .text:00400500                 lea     edx, byte_40099F
        .text:00400506                 call    sub_4005D0
        .text:0040050B                 push    offset byte_40099F
        .text:00400510                 call    console_print
        .text:00400515                 jmp     short password_ok
        .text:00400517 ; -----------------------------------------------
        .text:00400517
        .text:00400517 invalid_4:
        .text:00400517                 push    offset asc_400EF8 ; "\r\n"
        .text:0040051C                 call    console_print
        .text:00400521                 push    offset aAreYouFuckingW ; "  Are you fucking with me?"
        .text:00400526                 call    console_print
        .text:0040052B                 push    offset asc_400F17 ; "\r\n"
        .text:00400530                 call    console_print
        .text:00400535                 push    offset asc_400F1C ; "\r\n"
        .text:0040053A                 call    console_print
        .text:0040053F                 jmp     short exit_procedure
        .text:00400541 ; ----------------------------------------------
        .text:00400541
        .text:00400541 password_ok:
        .text:00400541                 push    offset dword_400984
        .text:00400546                 push    offset dword_4012C0
        .text:0040054B                 call    lstrcpyA
        .text:00400550                 push    offset byte_40098D
        .text:00400555                 push    offset dword_4012C0
        .text:0040055A                 call    lstrcatA
        .text:0040055F                 push    offset word_400996
        .text:00400564                 push    offset dword_4012C0
        .text:00400569                 call    lstrcatA
        .text:0040056E                 push    offset byte_40099F
        .text:00400573                 push    offset dword_4012C0
        .text:00400578                 call    lstrcatA
        .text:0040057D                 push    offset aSfsqSicriSfsq ; "OFSFn¦ßdµa¬OFSFn"
        .text:00400582                 call    sub_4005DA
        .text:00400587                 push    offset asc_400F20 ; "\r\n"
        .text:0040058C                 call    console_print
        .text:00400591                 push    offset aThanksForUsing ; "  Thanks for using our products! BRegar"...
        .text:00400596                 call    console_print
        .text:0040059B                 push    offset asc_400F4F ; "\r\n"
        .text:004005A0                 call    console_print
        .text:004005A5                 push    offset asc_400F54 ; "\r\n"
        .text:004005AA                 call    console_print
        .text:004005AF                 retn


The password is checked as 4 separate int16, thus decompiler didn't understand that values under thoses addreses are user input and treated those conditions as always false. So the password is checked against shorts: `0x3532, 0x3330, 0x3931, 0x3937`. Since x86 cpus use little endian byte order, we must reverse bytes to recover password: `0x32, 0x35, 0x30, 0x33, 0x31, 0x39, 0x37, 0x39 == "25031979"` and it is correct password:

    seurubucantasseeucolocavanagaiola
      Thanks for using our products! BRegards!

    Press any key to continue ...

but given file `flag.mocoh` is still encrypted... Let's check references to `ReadFile`:

     p sub_4005DA+3C   call    ReadFile
     p console_read+29 call    ReadFile

Second one in reading from standard input, so we ignore it, lets put breakpoint in first function:

![](assets/createfile.png)

oh! so it reads file `flag.mocoh` from folder `mocoh`. Let's put that file in the folder and run it again.

    $ cat mocoh/flag.mocoh
    3DS{4sS3mbly_r0cks!!}

    
###### Bartek aka bandysc 
