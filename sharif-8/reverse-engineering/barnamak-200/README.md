Barnamak
========

**Category:** Reverse Engineering, **Points:** 200, **Solves:** 67 **Our rank:** 13

```
Run the application and capture the flag!
```

### Write-up

In this challenge we are provided with an [android apk](Find_Flag.apk). I used [apkext](https://github.com/blukat29/apkext) to extract and decompile the application. While reading through the decompiled code I found this interesting bit of code:

```java
private static String iia(final int[] array, final String s) {
        String string = "";
        for (int i = 0; i < array.length; ++i) {
            string += (char)(array[i] - 48 ^ s.charAt(i % (s.length() - 1)));
        }
        return string;
    }

...

public void onClick(final DialogInterface dialogInterface, int n) {
                if (c.a() || c.b() || c.c()) { //check if phone is not rooted and we are on the correct position
                    n = (int)Math.round(ChallengeFragment.this.location.getLatitude());
                    final String access$100 = iia(new int[] { 162, 136, 133, 131, 68, 141, 119, 68, 169, 160, 49, 68, 171, 130, 68, 168, 139, 138, 131, 112, 141, 113, 128, 129 }, String.valueOf(n));
                    Toast.makeText(ChallengeFragment.this.getActivity().getBaseContext(), (CharSequence)access$100, 0).show();
                    ChallengeFragment.this.textViewLatitude1 = (TextView)ChallengeFragment.this.view.findViewById(2131558541);
                    ChallengeFragment.this.textViewLatitude1.setText((CharSequence)access$100);
                    System.exit(0);
                }
            }
...
```

Hmmm a xor cipher based on geolocation - what is the hardcoded location?

```java
public boolean b() {
        boolean b = false;
        final int int1 = Integer.parseInt("2C", 16);
        final int int2 = Integer.parseInt("5B", 16);
        final int intValue = Integer.valueOf(int1);
        final int n = -Integer.valueOf(int2);
        if (this.location != null) {
            if ((int)this.location.getLatitude() != intValue + 1 || (int)this.location.getLongitude() != n - 2) {
                Toast.makeText(this.context, (CharSequence)this.getString(2131165228), 0).show();
                return false;
            }
            ((Vibrator)this.context.getSystemService("vibrator")).hasVibrator();
            Toast.makeText(this.context, (CharSequence)this.getString(2131165227), 0).show();
            b = true;
        }
        return b;
    }
```

So the app expects us to be at 45N 93W. Using these coordinates to decrypt the hardcoded string in the `onClick` handler we obtain `Flag is MD5 Of Longtiude`
```
$ echo -n "-93" | md5sum
87a20a335768a82441478f655afd95fe
```
So the flag is `SharifCTF{87a20a335768a82441478f655afd95fe}`

###### By [gorbak25](https://github.com/grzegorz225) <gorbak25@gmail.com>
