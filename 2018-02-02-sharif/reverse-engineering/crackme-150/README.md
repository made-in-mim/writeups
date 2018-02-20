Crack me
===
**Category:** Reverse Engineering, **Points:** 150 + 8, **Solves:** 37, **Our rank:** 3 

> Find the password.

### Write-up

We are given Windows console application, which asks for password:

    > crackme.exe
    Enter Password:
    aaaa
    Try again

Let's find out what's inside assembly. There is a lot of useless code, which probably is here to "obfuscate code", like

    movss   xmm0, ds:dword_BE747C
    movss   [ebp+var_B4], xmm0
    movss   xmm0, ds:dword_BE7530
    movss   [ebp+var_B4], xmm0
    movss   xmm0, [ebp+var_B4]
    ucomiss xmm0, ds:dword_BE73F0
    lahf
    test    ah, 44h

And later this value is not used at all, after few minutes you learn to ignore them :-) What is interesting, there are few strings with debugger names: `OLLYDBG`, `idaq.exe`. Later `sub_BE1ED0` is called with those strings, which iterates over all processes and compare its names to detect if process with given name is running.

There is call to winapi `IsDebuggerPresent`, also `GetShellWindow`, `GetWindowThreadProcessId` and `NtQueryInformationProcess` are called to check who started current process. It looks like it also check how many cpu cycles have passed using `rdtsc` instruction - if user is using debugger it might have too high value.

If some anomalies are detected, some `char` array is modified, so it looks like it will be enough _not to_ modify the array using debugger.

Now let's find out when and _why_ "Try again" string is shown. The easiest way is to find references to `std::cout`. It is used in 3 places:

    Up	r	sub_402140+21F  mov     eax, std::cout
    Up	r	sub_402140+456  mov     edx, std::cout
    Up	r	_main+98        mov     eax, std::cout

The last one is "Enter password:" string, let's check first two. They are in the same function and depending on function argument value, first one or second one is called. When we put wrong password, `sub_892140` with non zero parameter is called. Let's change branch so that second text is printed (just change ZF flag value after comparison).

    Enter Password:
    7567
    Correct:Flag is Md5 Of Password

Ok, so flag is not contained in executable, it simply verifies if password is correct and it will be flag. So let's find out how is the argument value computed. This function is called with result of function `sub_891E70`, which is simple `strcmp`

    int sub_891E70(char *a1, char *a2)
    {
        signed int result;
    
        while ( *a1 == *a2 && *a1 && *a2 )
        {
            ++a1;
            ++a2;
        }
        if ( *a1 || *a2 )
            result = -1;
        else
            result = 0;
        return result;
    }

The second argument is constant string `whynxt` and the first one... well it is not that obvious. But when static analysis becomes not trivial, let's try dynamic analysis. After two tryouts, no doubt first parameter depends on user input, for `aaaaaaaaaa` it compares `whynxt` and `USRUSRUSRU`, for `bbbbbb` -> `whynxt` and `VPQVPQ`. So it looks like simple `xor` with cyclic sequence `423`. `whynxt ^ 423423 = CZJZJG` and it is actually correct password and as message in console says, the flag is `SharifCTF{md5("CZJZJG")} = SharifCTF{1854d4db8682639752588b732a50f3bb}`.


(Now, when we know what to look for, it was trivial to find where the xoring happens: few instructions eariler there is call to straightforward (after renaming symbols and removeing useless stuff) function:)

    string* xor_input(string *output, string input)
    {
        char key[3];
        int index;
        string input_copy;

        key[0] = '4';
        key[1] = '2';
        key[2] = '3';
        string_assign(&input_copy, &input);
        for ( index = 0; index < string_len(&input); ++index )
        {
            *string_operator[](&input_copy, index) = key[index % 3] ^ *string_operator[](&input, index);
        }
        string_move(output, &input_copy);
        return output;
    }	


To sum up, this task contanined few anti debugger tricks, but they were trivial to bypass at the result of detection was saved to variable and later it was added to xored characters. When we bypassed it, it wasn't hard to find correct password.


###### Bartek aka bandysc 
