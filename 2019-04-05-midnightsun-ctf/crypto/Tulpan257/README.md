> We made a ZK protocol with a bit of HFS-flair to it!
> > Download: (tulpan257.tar.gz)[https://s3.eu-north-1.amazonaws.com/dl.2019.midnightsunctf.se/529C928A6B855DC07AEEE66037E5452E255684E06230BB7C06690DA3D6279E4C/tulpan257.tar.gz]

Inside of the archive, there is this Sage file:
```python
flag = "XXXXXXXXXXXXXXXXXXXXXXXXX"
p = 257
k = len(flag) + 1

def prover(secret, beta=107, alpha=42):
    F = GF(p)
    FF.<x> = GF(p)[]
    r = FF.random_element(k - 1)
    masked = (r * secret).mod(x^k + 1)
    y = [
        masked(i) if randint(0, beta) >= alpha else
        masked(i) + F.random_element()
        for i in range(0, beta)
    ]
    return r.coeffs(), y

sage: prover(flag)
[141, 56, 14, 221, 102, 34, 216, 33, 204, 223, 194, 174, 179, 67, 226, 101, 79, 236, 214, 198, 129, 11, 52, 148, 180, 49] [138, 229, 245, 162, 184, 116, 195, 143, 68, 1, 94, 35, 73, 202, 113, 235, 46, 97, 100, 148, 191, 102, 60, 118, 230, 256, 9, 175, 203, 136, 232, 82, 242, 236, 37, 201, 37, 116, 149, 90, 240, 200, 100, 179, 154, 69, 243, 43, 186, 167, 94, 99, 158, 149, 218, 137, 87, 178, 187, 195, 59, 191, 194, 198, 247, 230, 110, 222, 117, 164, 218, 228, 242, 182, 165, 174, 149, 150, 120, 202, 94, 148, 206, 69, 12, 178, 239, 160, 7, 235, 153, 187, 251, 83, 213, 179, 242, 215, 83, 88, 1, 108, 32, 138, 180, 102, 34]
```


We can check, that the provided code implements Reed Solomon error correction
code. In general, we could solve this uniquely, if `alpha` was 41 or less, but
there is an algorithm that decodes all possible outputs for bigger alphas. It's
implemented in SageMath. After recovering the secret polynomial `masked`, we
invert it modulo $x^k+1$ and multiply it by the given polynomial `r`, to
reconstruct secret flag.
