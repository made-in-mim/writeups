OSS Signature
===

**Category:** Crypto **Points:** 100

[Download (original specs)](OSS_Signature.pdf)

### Write-up

This was one of two challenges during SharifCTF 2018 contest concerning the Ong-Schnorr-Shamir signature scheme and a pretty straightforward one.

In short, security of the OSS scheme is based on the hardness of solving equations of the form

<p align="center">
<img src="https://latex.codecogs.com/svg.latex?\inline&space;x^2&space;&plus;&space;ky^2&space;=&space;m&space;\pmod{n}" title="x^2 + ky^2 = m \pmod{n}" />
</p>

in variables <img src="https://latex.codecogs.com/svg.latex?\inline&space;x" title="x" /> and <img src="https://latex.codecogs.com/svg.latex?\inline&space;y" title="y" /> modulo a composite RSA modulus <img src="https://latex.codecogs.com/svg.latex?\inline&space;n" title="n" />. For a public key <img src="https://latex.codecogs.com/svg.latex?\inline&space;(n,&space;k)" title="(n, k)" /> a signature on a given message <img src="https://latex.codecogs.com/svg.latex?\inline&space;m" title="m" /> is any pair <img src="https://latex.codecogs.com/svg.latex?\inline&space;(x,&space;y)" title="(x, y)" /> for which the above relation holds. The problem of finding, say, <img src="https://latex.codecogs.com/svg.latex?\inline&space;x" title="x" /> for given <img src="https://latex.codecogs.com/svg.latex?\inline&space;y" title="y" /> and <img src="https://latex.codecogs.com/svg.latex?\inline&space;m" title="m" /> is equivalent to factoring (as in [the Rabin signature scheme](https://en.wikipedia.org/wiki/Rabin_cryptosystem)).

In the challenge, we are provided with a public key and two messages <img src="https://latex.codecogs.com/svg.latex?\inline&space;m_1" title="m_1" /> and <img src="https://latex.codecogs.com/svg.latex?\inline&space;m_2" title="m_2" /> with corresponding signatures <img src="https://latex.codecogs.com/svg.latex?\inline&space;(x_1,&space;y_1)" title="(x_1, y_1)" /> and <img src="https://latex.codecogs.com/svg.latex?\inline&space;(x_2,&space;y_2)" title="(x_2, y_2)" />, respectively. The goal is to craft a valid signature on the product of <img src="https://latex.codecogs.com/svg.latex?\inline&space;m_1" title="m_1" /> and <img src="https://latex.codecogs.com/svg.latex?\inline&space;m_2" title="m_2" />. This can be done with ease as the OSS scheme is malleable. Namely, the following identity holds over integers:

<p align="center">
<img src="https://latex.codecogs.com/svg.latex?\inline&space;(x_1^2&space;&plus;&space;ky_1^2)\cdot&space;(x_2^2&space;&plus;&space;ky_2^2)&space;=&space;x_3^2&space;&plus;&space;ky_3^2" title="(x_1^2 + ky_1^2)\cdot (x_2^2 + ky_2^2) = x_3^2 + ky_3^2" />
</p>

where

<p align="center">
<img src="https://latex.codecogs.com/svg.latex?\begin{align*}&space;x_3&space;&=&space;x_1&space;x_2&space;&plus;&space;ky_1&space;y_2&space;\\&space;y_3&space;&=&space;x_1&space;y_2&space;-&space;y_1x_2&space;\end{align*}" title="\begin{align*} x_3 &= x_1 x_2 + ky_1 y_2 \\ y_3 &= x_1 y_2 - y_1x_2 \end{align*}" />
</p>

After computing

```python
x3 = (x1 * x2 + k*y1*y2) % n
y3 = (x1 * y2 - y1 * x2) % n
```

we get that the pair <img src="https://latex.codecogs.com/svg.latex?\inline&space;(x_3,&space;y_3)" title="(x_3, y_3)" />, where

```
x3=3228192414578958851010842513154275809496752450843437198583166196901565071578144066800517210864829309956656172864622172889502523814134130877601254638400747755883616155295299435314390972047946113969350548381594633322779945307216665767237995638888452882989503186673207123359630734140939449837354851424900356484212983667331443801108560693455298625538140549843770730178132648956596007707374948190919655158210892858713252214782069457662864873988983041011930880072395421594443371267339482128681654521226571357238152202622389403367075320562466814355917951666554746996134626758309948472069549094989922908904448493268680406656
y3=518211291241825120181140993092343983770941887615321384844260199425792523199755041385119471907237849603159990373526771913427402452760004430627136113781638542767114113264285000466398106908417951520749203743404777034613190657137114341923476307793861309763818494314271906586789936425240207459021063361770273109412368272889165718779882091684440429454382783604840684421214437897887818039810429139216497093192387409059198251459001969178988926945417318424698086613437960638555659525583532581962406409400074841700047111118522735841781583725367240630089427247980009202413865204658013579671962256648081403159372023040686179602
```
is a valid signature on <img src="https://latex.codecogs.com/svg.latex?\inline&space;m_1m_2" title="m_1m_2" />. 
Submitting this signature to the verification system yielded the flag: `SharifCTF{aea9d91c12817a8f5a19b37ee9e1b1d6}`.