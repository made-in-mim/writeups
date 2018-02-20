Fifteen Puzzle
===
**Category:** Misc, PPC **Points:** 150, **Solves:** 126, **Our rank:** 6

> You are given 128 puzzles (https://en.wikipedia.org/wiki/15_puzzle)
>
> The ith puzzle determines the ith bit of the flag:
>
> \* 1 if the puzzle is soluble
>
> \* 0 if the puzzle is unsoluble
> 
> Implement is_soluble() below, and use the code to get the flag!
>
> **Note:** There is an important note on the News page about this challenge.
>
> ```
> def is_soluble(i):
>      return 0
> flag = ' '
> for i in range(128):
>     flag = ('1' if is_soluble(i) else '0') + flag
> print('SharifCTF{%016x}' % int(flag, 2))
> ```
> [Download](puzzles.txt)

### Note
The important note said, that bit-reversed flag will also be accepted.

### Write-up
The task asks us to check if given 15 puzzle is solvable. Basing on [geeksforgeeks link](https://www.geeksforgeeks.org/check-instance-15-puzzle-solvable/) we can implement it in Python with ease. Here's a full [script](script.py) that parses the input and solves the task.

Flag is `SharifCTF{52d3b36b2167d2076b06d8101582b7af}.`
