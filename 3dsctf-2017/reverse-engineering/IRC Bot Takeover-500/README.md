Ransomware
===
**Category:** IRC Bot Takeover, **Points:** 500, **Solves:** 20

> WARNING! DON'T EXECUTE THIS SAMPLE IN YOUR OWN PERSONAL MACHINE!!!
>
> Update: We had some problems with a specific step of the challenge (still possible to solve, but more hard) and we updated the binary. The new file has the old version, but you only need the new to solve.

### Write-up

This write-up is about older version of the task. 

Both ransomaware and w32.killah tasks were about xoring strings so let's try to find xoring here also, after checking all functions (only few in executable), we find two functions that do xoring same as in two other tasks:

    void xor(char byte, char* text, int len)
    {
        do
        {
            *text++ ^= byte;
            --len;
        }
        while ( len );
    }

    void xor_add(char byte, char* text, int len)
    {
        do
        {
            *text += byte;
            *text++ ^= byte;
            --len;
        }
        while ( len );
    }

Now, let's find references to them - luckily only 8 in total. Checking them all gives result:

    char part1[] = "%<EmqhiYUi0deY\\";
    char part2[] = "mckW,sSWisWdak3!u";
    
    xor_add('E', part1, 15);
    xor_add('B', part1, 15);
    xor_add('@', part2, 17);
    xor_add('D', part2, 17);
    printf("%s%s\n\n", part1, part2);

    // 3DS{who_co0ls_duck_4sS_is_lak3!}
    
###### Bartek aka bandysc 
