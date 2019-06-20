# xiap
A lot of XARK in a little pond.

$ curl -u ${client_id}:${client_secret} -XPOST http://127.0.0.1:5000/oauth/token -F grant_type=password -F username=${username} -F password=valid -F scope=profile

{"client_id": "VBX27CNWNEQaZ60EAyujVtYv", "client_id_issued_at": 1560988156, "client_secret": "cfPcwZM41pJnfWV1VcAZu2pj7VCG3605sRHypEN0FZ35KPw7", "client_secret_expires_at": 0}
{"client_name": "Hi", "client_uri": "https://fundacionzt.org/", "contacts": [], "grant_types": ["authorization_code", "password"], "jwks": null, "jwks_uri": null, "logo_uri": null, "policy_uri": null, "redirect_uris": ["https://fundacionzt.org/"], "response_types": ["code"], "scope": "profile", "token_endpoint_auth_method": "client_secret_basic", "tos_uri": null}

curl -X POST -d "client_id=VBX27CNWNEQaZ60EAyujVtYv&client_secret=cfPcwZM41pJnfWV1VcAZu2pj7VCG3605sRHypEN0FZ35KPw7&grant_type=password" http://127.0.0.1:5000/oauth/token
