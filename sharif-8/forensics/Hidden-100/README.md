Hidden
===
**Category:** Forensics **Points:** 100, **Solves:** 122, **Our rank:** 70

> Find the hidden process.
>  
> The flag is SharifCTF{MD5(Process id)}.
>
> [Download](dump.zip)

### Write-up
In the task we are given a memory dump. We're going to use a nifty tool called [Volatility](https://github.com/volatilityfoundation/volatility).

`python vol.py pslist -f dump` returns a list of processes, that are still running, and aren't hidden.

```
Volatility Foundation Volatility Framework 2.6
Offset(V)  Name                    PID   PPID   Thds     Hnds   Sess  Wow64 Start                          Exit                          
---------- -------------------- ------ ------ ------ -------- ------ ------ ------------------------------ ------------------------------
0x81242a00 System                    4      0     57      263 ------      0                                                              
0xff391900 smss.exe                548      4      3       19 ------      0 2018-01-28 16:59:16 UTC+0000                                 
0xff36bda0 csrss.exe               620    548     12      305      0      0 2018-01-28 16:59:19 UTC+0000                                 
0xff39f608 winlogon.exe            644    548     19      537      0      0 2018-01-28 16:59:20 UTC+0000                                 
0xff391488 services.exe            688    644     16      353      0      0 2018-01-28 16:59:24 UTC+0000                                 
0xff390410 lsass.exe               700    644     20      349      0      0 2018-01-28 16:59:25 UTC+0000                                 
0xff378798 vmacthlp.exe            856    688      1       25      0      0 2018-01-28 16:59:34 UTC+0000                                 
0xff3a59c0 svchost.exe             900    688     17      211      0      0 2018-01-28 16:59:39 UTC+0000                                 
0xff3bc378 svchost.exe             988    688     11      235      0      0 2018-01-28 16:59:47 UTC+0000                                 
0xff3cb6e0 svchost.exe            1024    688     54     1107      0      0 2018-01-28 16:59:51 UTC+0000                                 
0xff2077a8 svchost.exe            1188    688      4       57      0      0 2018-01-28 16:59:53 UTC+0000                                 
0xff3a7878 svchost.exe            1236    688     10      167      0      0 2018-01-28 16:59:56 UTC+0000                                 
0xff1bbcf0 spoolsv.exe            1508    688     11      140      0      0 2018-01-28 17:00:19 UTC+0000                                 
0xff1b1020 explorer.exe           1576   1444     12      404      0      0 2018-01-28 17:00:24 UTC+0000                                 
0xff1aa9f0 svchost.exe            1604    688      4      105      0      0 2018-01-28 17:00:25 UTC+0000                                 
0xff197b20 svchost.exe            1692    688      3       94      0      0 2018-01-28 17:00:31 UTC+0000                                 
0x811244c0 rundll32.exe            396   1576      4       70      0      0 2018-01-28 17:02:48 UTC+0000                                 
0xff1c30e8 wscntfy.exe             920   1024      1       31      0      0 2018-01-28 17:05:09 UTC+0000          
```
Meanwhile, `python vol.py psscan -f dump` also includes hidden or already closed processes.
```
Volatility Foundation Volatility Framework 2.6
Offset(P)          Name                PID   PPID PDB        Time created                   Time exited                   
------------------ ---------------- ------ ------ ---------- ------------------------------ ------------------------------
0x000000000096c0e8 wscntfy.exe         920   1024 0x007002c0 2018-01-28 17:05:09 UTC+0000                                 
0x00000000010eb4c0 rundll32.exe        396   1576 0x007001a0 2018-01-28 17:02:48 UTC+0000                                 
0x0000000001209a00 System                4      0 0x00359000                                                              
0x0000000001bbd488 services.exe        688    644 0x00700080 2018-01-28 16:59:24 UTC+0000                                 
0x0000000001bbd900 smss.exe            548      4 0x00700020 2018-01-28 16:59:16 UTC+0000                                 
0x0000000001c279c0 svchost.exe         900    688 0x00700100 2018-01-28 16:59:39 UTC+0000                                 
0x0000000001c58798 vmacthlp.exe        856    688 0x007000c0 2018-01-28 16:59:34 UTC+0000                                 
0x0000000001de4878 svchost.exe        1236    688 0x00700180 2018-01-28 16:59:56 UTC+0000                                 
0x0000000001e64350 vmtoolsd.exe        404   1576 0x00700260 2018-01-28 17:02:50 UTC+0000                                 
0x0000000001e6d608 winlogon.exe        644    548 0x00700060 2018-01-28 16:59:20 UTC+0000                                 
0x0000000001ebe168 cmd.exe            1704   1576 0x007002a0 2018-01-28 17:30:47 UTC+0000   2018-01-28 17:34:00 UTC+0000  
0x0000000001ecd378 svchost.exe         988    688 0x00700120 2018-01-28 16:59:47 UTC+0000                                 
0x0000000001fbd6e0 svchost.exe        1024    688 0x00700140 2018-01-28 16:59:51 UTC+0000                                 
0x0000000001fbe410 lsass.exe           700    644 0x007000a0 2018-01-28 16:59:25 UTC+0000                                 
0x00000000021a7da0 csrss.exe           620    548 0x00700040 2018-01-28 16:59:19 UTC+0000                                 
0x00000000025b7020 explorer.exe       1576   1444 0x007001e0 2018-01-28 17:00:24 UTC+0000                                 
0x0000000002dbb448 wmiprvse.exe        908    900 0x00700240 2018-01-28 17:32:51 UTC+0000   2018-01-28 17:34:22 UTC+0000  
0x0000000002e7eb20 svchost.exe        1692    688 0x00700220 2018-01-28 17:00:31 UTC+0000                                 
0x000000000308d9f0 svchost.exe        1604    688 0x00700200 2018-01-28 17:00:25 UTC+0000                                 
0x00000000031b1cf0 spoolsv.exe        1508    688 0x007001c0 2018-01-28 17:00:19 UTC+0000                                 
0x00000000039347a8 svchost.exe        1188    688 0x00700160 2018-01-28 16:59:53 UTC+0000  
```

Comparing those two lists, we see that there are three processes that differ.
```
0x0000000001e64350 vmtoolsd.exe        404   1576 0x00700260 2018-01-28 17:02:50 UTC+0000 
0x0000000001ebe168 cmd.exe            1704   1576 0x007002a0 2018-01-28 17:30:47 UTC+0000   2018-01-28 17:34:00 UTC+0000  
0x0000000002dbb448 wmiprvse.exe        908    900 0x00700240 2018-01-28 17:32:51 UTC+0000   2018-01-28 17:34:22 UTC+0000  
```

Two of those are already closed, that leaves us with `vmtoolsd.exe`, which has process ID equal to `404`.

The flag is `SharifCTF{4f4adcbf8c6f66dcfc8a3282ac2bf10a}`.
