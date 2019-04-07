> Someone told me not to use DSA, so I came up with this.

> > settings Service: nc ezdsa-01.play.midnightsunctf.se 31337 

> > Download: [EZDSA.tar.gz](https://s3.eu-north-1.amazonaws.com/dl.2019.midnightsunctf.se/529C928A6B855DC07AEEE66037E5452E255684E06230BB7C06690DA3D6279E4C/EZDSA.tar.gz)

In the archive, there is following Python file:

```python
from hashlib import sha1
from Crypto import Random
from flag import FLAG


class PrivateSigningKey:

    def __init__(self):
        self.gen = 0x44120dc98545c6d3d81bfc7898983e7b7f6ac8e08d3943af0be7f5d52264abb3775a905e003151ed0631376165b65c8ef72d0b6880da7e4b5e7b833377bb50fde65846426a5bfdc182673b6b2504ebfe0d6bca36338b3a3be334689c1afb17869baeb2b0380351b61555df31f0cda3445bba4023be72a494588d640a9da7bd16L
        self.q = 0x926c99d24bd4d5b47adb75bd9933de8be5932f4bL
        self.p = 0x80000000000001cda6f403d8a752a4e7976173ebfcd2acf69a29f4bada1ca3178b56131c2c1f00cf7875a2e7c497b10fea66b26436e40b7b73952081319e26603810a558f871d6d256fddbec5933b77fa7d1d0d75267dcae1f24ea7cc57b3a30f8ea09310772440f016c13e08b56b1196a687d6a5e5de864068f3fd936a361c5L
        self.key = int(FLAG.encode("hex"), 16)

    def sign(self, m):

        def bytes_to_long(b):
            return long(b.encode("hex"), 16)

        h = bytes_to_long(sha1(m).digest())
        u = bytes_to_long(Random.new().read(20))
        assert(bytes_to_long(m) % (self.q - 1) != 0)

        k = pow(self.gen, u * bytes_to_long(m), self.q)
        r = pow(self.gen, k, self.p) % self.q
        s = pow(k, self.q - 2, self.q) * (h + self.key * r) % self.q
        assert(s != 0)

        return r, s
```

The netcat service allows signing messages. We want to know the `key`, as it is the
flag with a simple encoding. Take any message `m` (suppose it's already encoded as a number).
Since `r`, `s`, `p`, `q` and `h` are known (`h = SHA1` of our message), we just need to know `k` in order to solve for `key`.
As `q` is prime, `k^(q-2) % q == k^(-1) % q` (by Little Fermat's Theorem), so the
last equation tells us that
``
key == (s*k - h) * r^(-1) % q
``
Note that if `key >= q`, then we stand no chance recovering it - we need to
assume it's correct in size.

All that needs to be done is to recover `k`. 

As we know, `k == gen^(um) % q == (gen^m)^u % q`. `u` is random, so
in the worst case, we know nothing about `k`. But there is a hint - `m`
cannot be a multiple of `q - 1`. This is, because of Fermat's Little
Theorem (once again!), for any `x` nondivisible by `q`, `x^(q-1) % q == 1`. But there might be other numbers apart from `q-1` which satisfy this property. Indeed, we may
check that `gen^((q-1)/2) % q ==  1` (for this paricular `gen`). This means
that for message `m = (q-1)/2`, we have `k == (gen^m)^u % q == 1^u % q == 1`. This is sufficient to recover `key`.

Note that we didn't just have "luck" - for any `g`, and for any prime `q > 2`, it is true that `g^((q-1)/2) % q` is either `1` or `-1`. If it were `-1`, we'd just need to consider 2 cases for `u` odd and `u` even.

So, let's try to recover the flag:
```python3
>>> import base64
>>> q = 0x926c99d24bd4d5b47adb75bd9933de8be5932f4b
>>> msg = (q-1)//2
>>> msg_encoded = msg.to_bytes((msg.bit_length()+7)//8, 'big') 
>>> base64.b64encode(msg_encoded)
b'STZM6SXqato9bbrezJnvRfLJl6U='
```

```
Welcome to Spooners' EZDSA
Options:
1. Sign protocol
2. Quit
1
Enter data:
STZM6SXqato9bbrezJnvRfLJl6U=
(698847418084580852997663919979623019513778951409L, 629758878500372559472644038362239654961033814558L)
```

```python3
>>> from gmpy2 import invert
>>> from hashlib import sha1
>>> r, s = (698847418084580852997663919979623019513778951409, 629758878500372559472644038362239654961033814558)
>>> q = 0x926c99d24bd4d5b47adb75bd9933de8be5932f4b
>>> msg = (q-1)//2
>>> msg_encoded = msg.to_bytes((msg.bit_length()+7)//8, 'big')
>>> h = int.from_bytes(hashlib.sha1(msg_encoded).digest(), 'big')
>>> h = int.from_bytes(sha1(msg_encoded).digest(), 'big')
>>> key = int((s - h) * invert(r, q) % q)
>>> key.to_bytes((key.bit_length()+7)//8, 'big')
b'th4t_w4s_e4sy_eh?'
```
