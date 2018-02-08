Hidden Input
============

## Task description
Can you log in?

## Solution
The challenge greets us with a login screen.

![](https://i.imgur.com/SW9KwbH.png)

Upon inspecting the page source, a hidden input field `debug` with value `0` can be found.

![](https://i.imgur.com/XUM9SAW.png)

After changing its value to `1` and submitting the form, the following debug output appears:

![](https://i.imgur.com/nmdKr4t.png)

The username needed to bypass the authentication should therefore be `') OR 1=1 -- `. After inputting it as the username and submitting the form, the flag is found.

![](https://i.imgur.com/uGrn3aC.png)

