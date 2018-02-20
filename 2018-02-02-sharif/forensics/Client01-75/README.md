Client01
===
**Category:** Forensics **Points:** 75, **Solves:** 145, **Our rank:** 32

> Attached file is the homepage of the client01. He knows the flag.
>
> [Download](client01.tar.gz)

### Write-up
In the task we are given a file structure of mysterious client01. There's nothing in visible files, let's try searching for `sharif` or `Sharif`.

`grep -r Sharif .` returns nothing, but `grep -r sharif .`does:

```
Binary file ./.thunderbird/5bd7jhog.default/global-messages-db.sqlite matches
./.thunderbird/5bd7jhog.default/ImapMail/imap.gmail.com/[Gmail].sbd/Sent Mail:        for <contest@cert.sharif.edu>
./.thunderbird/5bd7jhog.default/ImapMail/imap.gmail.com/[Gmail].sbd/Sent Mail:To: contest@cert.sharif.edu
./.thunderbird/5bd7jhog.default/ImapMail/imap.gmail.com/[Gmail].sbd/Trash:        for <contest@cert.sharif.edu>
./.thunderbird/5bd7jhog.default/ImapMail/imap.gmail.com/[Gmail].sbd/Trash:To: contest@cert.sharif.edu
```

In `Sent Mail` file there's nothing interesting, but in `Trash` we find this:

```
Received: by 10.46.97.9 with HTTP; Tue, 23 Jan 2018 20:54:23 -0800 (PST)
From: dev null <devnull2019@gmail.com>
Date: Wed, 24 Jan 2018 08:24:23 +0330
Message-ID: <CAOLu_Eji_fy5G7zkTYC5D=0Df9hL50fyQyGqp-CJ3FX+MnuqrQ@mail.gmail.com>
Subject: flag
To: devnull2018@gmail.com
Content-Type: multipart/alternative; boundary="94eb2c1a636603369f05637e75da"

--94eb2c1a636603369f05637e75da
Content-Type: text/plain; charset="UTF-8"

http://www.filehosting.org/file/details/720884/file

--94eb2c1a636603369f05637e75da
Content-Type: text/html; charset="UTF-8"

<div dir="ltr"><a style="color:rgb(0,187,0);text-decoration:none" href="http://www.filehosting.org/file/details/720884/file" target="_blank">http://www.filehosting.org/<wbr>file/details/720884/file</a></$

--94eb2c1a636603369f05637e75da--
```

If we visit [filehosting link](http://www.filehosting.org/file/details/720884/file) we can request a download and after we get [this file](data).

` file data` says there's nothing interesting in this file, let's look at the headers:

```
00000000   89 4E 47 0D  0A 1A 0A 00  00 00 0D 49  48 44 52 00  .NG........IHDR.
00000010   00 03 E8 00  00 00 C8 04  03 00 00 00  89 C9 D6 7C  ...............|
00000020   00 00 00 1B  50 4C 54 45  00 00 00 FF  FF FF 5F 5F  ....PLTE......__
00000030   5F 9F 9F 9F  BF BF BF DF  DF DF 7F 7F  7F 3F 3F 3F  _............???
00000040   1F 1F 1F AD  A0 D6 E1 00  00 00 09 70  48 59 73 00  ...........pHYs.
00000050   00 0E C4 00  00 0E C4 01  95 2B 0E 1B  00 00 0E FC  .........+......
00000060   49 44 41 54  78 9C ED 9C  CF 73 1B 37  12 85 87 3F  IDATx....s.7...?
```

This looks like a corrupted `PNG` header, with `P` missing, after fixing it we're greeted by an image with a flag:

![](flag.png)

Well, at least half of it, but we can see all we need, and the flag is `SharifCTF{43215f0c5e005d4e557ddfe3f2e57df0}`
