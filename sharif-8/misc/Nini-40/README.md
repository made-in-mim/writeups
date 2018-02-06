Nini
===
**Category:** Misc, **Points:** 40 + 2, **Solves:** 366, **Our rank:** 3

> What is the most important prize she honored?
>
> The flag is SharifCTF{MD5(lowercase(Prize name))}.
>
> [Download](Nini.jpg)

### Write-up

In the task we are given a picture

![](Nini.jpg)

After plugging it into Google Reverse Search, the first link that pops up is a [Wikipedia page](https://en.wikipedia.org/wiki/Maryam_Mirzakhani) of a woman we are looking for. She won a `Fields Medal`.

So we just need to find MD5 of `fields medal`, which gives us the flag `SharifCTF{537cd12c5f65d15dd11cc5d7f27127a8}`. 
