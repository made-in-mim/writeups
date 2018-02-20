Hello Rules
===
**Category:** Web, **Points:** 10, **Solves:** 651, **Our rank:** 6

> Find the flag in rule page

### Write-up

Just do exactly what the task says, go to a rule page, and at the bottom of the page we find this:


    Hello rules challenge

    The flag of this challenge is SharifCTF{MD5(lowercase(Hello_Rules))}


So we just need to find MD5 of `hello_rules`, which gives us the flag `SharifCTF{053e3df6d82735fa4f708f3d61f2c903}`. 
