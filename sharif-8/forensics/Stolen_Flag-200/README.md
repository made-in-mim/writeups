Stolen Flag
===
**Category:** Forensics **Points:** 200, **Solves:** 15, **Our rank:** 15

> This PC is attacked. The flag is stolen.
> Follow this link

### Write-up
Given file is 800MB zip of a single >5GB Mini.vmdk file. To download that and
find necessary disk space was apparently a turn off for us, as we solved this problem very last :)

[VMDK](https://en.wikipedia.org/wiki/VMDK) is a file format for virtual machines hard drives.
It's not too pleasant to work with on Linux, so let's first convert it into something more usable.


```
$ qemu-img convert -O raw Mini.vmdk mini.img
```

Now we can inspect the image and find partitions:
```
# kpartx -av mini.img
loop0p1 : 0 1099200 /dev/loop0 1025011
loop0p2 : 0 2 /dev/loop0
loop0p5 : 0 4505600 /dev/loop0 1024063
```

The first one turns out to be ext4, the last one swap, and the middle one something small and strange, maybe just some kpartx artifact.
We can mount the first one and see pretty much the usual root fs layout

```
# mount /dev/loop0p1 p1/
# ls p1/
bin   dev         etc     initrd.img lib    lib64   lost+found  mnt  proc  sys      usr
boot  home        media   opt        root   sbin    srv         tmp  var   vmlinuz

```

The filesystem however is quite empty - many usual files are missing. Root's `.bash_history` indicates why this may be the case,
containing mostly multiple `rm -rf`, but on uninteresting directories like `/usr/share/icons/something`.

Let's turn to swap space then. After failed attempt to inspect swap with [volatility framework](https://github.com/volatilityfoundation/volatility),
googling lead me to [swap_digger](https://github.com/sevagas/swap_digger). This seems to be a quite simple tool for looking for interesting patterns in swap file.
Example output from author's github:
![Swap_digger example output] (https://raw.githubusercontent.com/sevagas/swap_digger/master/assets/swap_digger_extended.png)

Running it did not give us anything interesting though - no passwords, some ip addresses, some usual http urls.
Well, and a list of organizers' windows computers at the time of creating the challenge xD :

```
[+] TOP 30 smb shares
  ->       3 smb://AMIRHOSEIN-LAPT/
  ->       3 smb://AMIRHOSEIN-LATI/
  ->       3 smb://DELL-PC/
  ->       3 smb://HIVACOMPUTER/
  ->       3 smb://HS-PC/
  ->       3 smb://JAVAD-PC/
  ->       3 smb://KARANEH-PC009/
  ->       3 smb://MOHAMMAD/
  ->       3 smb://MOHSEN-PC/
  ->       3 smb://MREZA/
  ->       3 smb://PC-2/
  ->       2 smb://REZA-PC/
```

The idea of looking for urls seemed appealing though, and swap digger only printed out the ones appearing more often. If someone were to "steal" a flag from this pc,
putting it on some public clipboard service sounds like a reasonable idea, and he definitely would not do this 10 times. Let's look for more urls then:

```
# strings /dev/loop0p5 | egrep 'https?://'
```

This gave me a few hundreds of urls, with `https://gist.github.com/clipboardstolenthings` boldly standing out.
The link is now dead, but it contained a few gists, including one with the flag: `SharifCTF{522bab2661c00e672cf1af399d6055cd}`

In hindsight, possibly simple `strings Mini.vmdk | egrep 'https?://'` would work as well.
