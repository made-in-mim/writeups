Find Me
===

**Category:** Reverse Engineering, **Points:** 250 + 25, **Solves:** 3 

> Run and capture the flag!

### Write-up


We are given windows executable, which only shows message:

    ---------------------------
    Fail
    ---------------------------
    try again 
    ---------------------------
    OK   
    ---------------------------

and shut down. Let's see what's inside. Quick peak at disassembled code shows it was written in c++ with a lot of winapi calls so the generated assembly is a bit of mess. As usually in such tasks, I've start from the (theoretical) end - the message box. There is imported `MessageBoxW` function, let's check references to this function. It turns out there are two calls:

    Up    p    sub_403E40+76A  call    ds:MessageBoxW 
    Up    p    aa+482          call    ds:MessageBoxW

Interestingly, the executable is stripped, but the name of second function is known, so I've looked at exports and it turned out it is exported function in the binary. And there are no direct calls to `aa`. "Maybe there is some magic to jump there" I thought and returned to analysing first MessageBox.

    if ( v17 )
    {
      MessageBoxW(0, L"try again ", L"Fail", 0);
    }

ok, let's check where is `v17` set and it turnes out... it is set to const value `1` at the beginning of the function. And function at offset `0x3E40`, which shows the message box is called always so it looks like we should really focus on `aa` function. 

So at this point I've jumped to analyse `aa`. Function was doing a lot of operations on `strings` and `wstrings`. I really wanted to call that function, however simple jump in debugger wasn't enough due to passed variables, so I started thinking how to call it from external application - after all it was exported function. If it was `dll` library, it would be simple - I would just use `LoadLibrary` and `GetProcAddress` from Windows API to load dll into memory space and then get address to function and call it. But it was `exe` so this trick doesn't work. While calling exported function from exe is not as easy, it turned out not to be _that_ hard. The trick was to create `dll`, _inject_ it into `exe` and then call the function (pretty oposite to creating exe and loading given `dll` into it). [There are multiple ways to inject dll into binary](https://security.stackexchange.com/questions/58009/ways-to-inject-malicious-dlls-to-exe-file-and-run-it), but I've decided simply to use existing injector so that I had just to write my `dll`. IDA claimed this function takes two arguments, so at the beginning I just passed quite big 0 arrays.

    // dllmain.cpp : Defines the entry point for the DLL application.
    #include "stdafx.h"
    #include <string>

    typedef int(__cdecl *aa_t)(void*, void*);

    BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved)
    {
        HINSTANCE hGetProcIDDLL = GetModuleHandle(NULL);

        if (hGetProcIDDLL != NULL)
        {
            char zeros1[300], zeros2[300];

            memset(zeros1, 0, sizeof(zeros1));
            memset(zeros2, 0, sizeof(zeros2));

            aa_t aa = (aa_t)GetProcAddress(hGetProcIDDLL, "aa");
            aa(zeros1, zeros2);

            MessageBoxA(0, "test", "test", 0);
        }

        return TRUE;
    }

![](assets/injector.png)

Injecting and... it looks like it worked! No crash, message box shown. Setting breakpoint inside `aa` in the debugger confirmed it - my dll was loaded to process address space and it called exported function.

In `aa` pseudo code one function was definietly standing out - `MessageBoxW`, however this time text and caption weren't directly readable - it looked like it is decoded somewhere

    if ( !_wcsicmp(Str1, v8) )
        dword_105AB18 = 1;
    if ( *(_BYTE *)sub_1035690(0) == 70 && *(_BYTE *)sub_1035690(3) == 103 )
        dword_105AB14 = 1;
    while ( 1 )
    {
        if ( *(_BYTE *)sub_1035690(1) == 108 && *(_BYTE *)sub_1035690(2) == 97 )
            dword_105AB1C = 1;
        if ( dword_105AB18 != 1 )
            break;
        if ( dword_105AB14 == 1 )
        {
            if ( dword_105AB1C == 1 )
            {
                v11 = 0;
                v10 = (const WCHAR *)sub_1035990(&unk_105AB24);
                v6 = (const WCHAR *)sub_1035990(&v40);
                MessageBoxW(0, v6, v10, v11);
                break;
            }
        }
    }

Ok, so messagebox is shown when `dword_105AB1C == 1`, `dword_105AB14 == 1` and `dword_105AB18 == 1`. Before we try to anlyse when those conditions are met, let's try to change resulting branch in debugger so that _some_ message box actually pops out. We can either edit memory in debugger and put `1` under those addresses or toggle `ZF` flag after `cmp` instruction.


    ---------------------------
    
    ---------------------------
    Flag is First Argument Of function
    ---------------------------
    OK   
    ---------------------------

I think it is self explaining, but this also means more work is needed under investingating what's going in the code. Especially that it is not obvious what is first argument and how it should be generated. After few minutes of fruitless work, I've decided to return to `WinMain`, because I thought it might be really called somewhere there and calling it from my dll is senseless. Luckily quickly I had found string `Hex key must have an even number of characters`, since it was really characteristic I have googled it and first result was... [gist with simple rc4 implementation!](https://gist.github.com/Mjiig/2727751). I have compared assembly and this code and it was _exactly_ the same code, but `argc` and `argv` in function `parseargs` are always `NULL`, so this program doesnt load anything. And even if it loaded something, it wasn't later used for anything. It confirmed that this code doesn't do anything usefull. It was only to slow us down :-). But it also let me rename some symbols operating on `std::string`, which made reading `aa` easier!

So after renaming some symbols using this gist, I've returned to analysing `aa` and the code was much more readable

    if ( *(_BYTE *)sub_1035690(0) == 70 && *(_BYTE *)sub_1035690(3) == 103 )

became

    if ( *string__char_at(&some_string, 0) == 'F' && *string__char_at(&some_string, 3) == 'g' )
    
and

    if ( *(_BYTE *)sub_1035690(1) == 108 && *(_BYTE *)sub_1035690(2) == 97 )
    
became

    if ( *string__char_at(&some_string, 1) == 'l' && *string__char_at(&some_string, 2) == 'a' )
    
So somehow we must put `Flag` string into `some_string` variable. Few lines above there is:

    string__assign_cstring(&v9, second_function_argument);
    sub_1032A50(&some_string, v9);
    
That's mean `second_function_argument` must be `char*` (because `string__assign_cstring` is used on it), it is then assigned to string at `ebp-0x15C` and some function is then called with this argument and `some_string`, which is then compared to "Flag". After some work on renaming symbols and types, it turns out to be really straightforward:


    string *__cdecl sub_1032A50(string *a1, string a2)
    {
        char key[3]; // [esp+Ch] [ebp-30h]
        int index; // [esp+10h] [ebp-2Ch]
        string xored; // [esp+14h] [ebp-28h]

        key[0] = '6';
        key[1] = '2';
        key[2] = '3';
        string__copy_string(&xored, &a2);
        for ( index = 0; index < string__length(&a2); ++index )
        {
            *string__char_at(&xored, index) = key[index % 3u] ^ *string__char_at(&a2, index);
        }
        string__move(a1, &xored);
        return a1;
    }
    
This function simply xors second argument with values `'6'`, `'2'` and `'3'`, then returns new xored string. Let's check if it is true and instead of array of zeros, pass as second argument string `{'F' ^ '6', 'l' ^ '2', 'a' ^ '3', 'g' ^ '6'}`. It really works! Tho as it will finally turn out this second argument doesn't really matter - it is all about the first argument and check:

    Str1 = aPRq;
    wstring__new(&some_wstring);
    wstring__assign_wcstring(&some_wstring, first_argument);

    (...)

    v8 = wstring__wcstr(&v40);
    if ( !_wcsicmp(Str1, v8) )
        dword_105AB18 = 1;

`Str1` is const wide string (`wchar_t*`) `50 00 5E 00 52 00 51 00 08 00 13 00 4F 00 02 00 46 00 16 00 56 00 03 00 58 00 57 00 00 00`, which contains only few random readable chars. And `v40`... because it was originally c++ code with std::strings and std::wstrings, decompiler wasn't really helpful to say where the value comes from. But if constant `wchar_t*` is simply compared to some other wide string and the first argument is `wchart_*`... it was worth trying to simply send that string to `aa` function. No message box, so I have put breakpoint in `_wcsicmp` and...

![](assets/youdone.png)

Wow! Sending those bytes resulted in comparing those bytes against readable string: 'flag: y0u d0ne'. So maybe flag is `SharifCTF{md5({0x50, 0x00, 0x5E, 0x00, 0x52, 0x00, 0x51, 0x00, 0x08, 0x00, 0x13, 0x00, 0x4F, 0x00, 0x02, 0x00, 0x46, 0x00, 0x16, 0x00, 0x56, 0x00, 0x03, 0x00, 0x58, 0x00, 0x57, 0x00, 0x00, 0x00})}`? No, it doesn't work... Let's check what if I send `flag: y0u d0ne`.

    // dllmain.cpp : Defines the entry point for the DLL application.
    #include "stdafx.h"

    typedef int(__cdecl *aa_t)(wchar_t*, char*);

    BOOL APIENTRY DllMain( HMODULE hModule,  DWORD  ul_reason_for_call, LPVOID lpReserved)
    {
        HINSTANCE hGetProcIDDLL = GetModuleHandle(NULL);

        if (hGetProcIDDLL != NULL)
        {
            wchar_t arg1[] = L"flag: y0u d0ne";
            char arg2[5] = { 'F' ^ '6', 'l' ^ '2', 'a' ^ '3', 'g' ^ '6'};

            aa_t FnPtr = (aa_t)GetProcAddress(hGetProcIDDLL, "aa");
            FnPtr(arg1, arg2);
        }
        return TRUE;
    }

Bingo! Now message box shows up without modifying any memory. It also means that first argument was xored with... that's right, also with array `{'6', '2', '3'}`. Final check if flag is `SharifCTF{md5("flag: y0u d0ne")} = SharifCTF{195f38514b7c9cc49abb3f70d9fd7a57}` aaand it is correct flag! We are done. No doubt creating our own `dll` and injecting it into exe to call `aa` wasn't necessary at all, but it was fastest way for me to call `aa` with any parameters. After renaming symbols this task was easy, but before decompiled code wasn't really readable, so even though I've wasted some time understanding RC4 implementation, later it helped me with decompiling `aa` function.



###### Bartek aka bandysc 
