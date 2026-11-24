# evo-licsrv

Fake licence server for **EVO EXTERNAL v2.0** (EVOLUTION / ROS external).

EVO's activation path soft-validates: it POSTs `{"key","machineId"}` to
`<endpoint>/activate`, and any response JSON carrying a truthy `"success"`
key flips the binary's auth state to *licensed* through its own code —
no signature, no challenge, no key checks.

This server answers exactly that. Point any EVO 2.0 copy at it and the
licence pane disappears, the status reads licensed, and the payload gate
opens. Any key in the activation box works.

## Deploy on Render (free)

1. Fork or use this repo directly
2. Render dashboard → **New +** → **Blueprint** → pick the repo → **Apply**
   (or manually: New Web Service, runtime **Python**, build command empty,
   start command `python evo_licsrv.py`, health check path `/health`)
3. Render gives you a URL like `https://evo-licsrv-xxxx.onrender.com`

No dependencies — Python stdlib only.

## Use it

One environment variable on the machine running EVO:

```
setx EVO_AUTH_ENDPOINT "https://evo-licsrv-xxxx.onrender.com"
```

Then start `EVO.exe`. Enter anything in the licence box and hit **ACTIVATE**.

## Run locally

```
python evo_licsrv.py            # http://127.0.0.1:8007/activate
```

Then `set EVO_AUTH_ENDPOINT=http://127.0.0.1:8007` before launching EVO.

## Endpoints

| Method | Path        | Response |
|---|---|---|
| POST   | `/activate` | `200 {"success":true,"expiresAt":4102444800000,"serverNow":<now>}` |
| GET    | `/health`   | `200 {"service":"evo-licsrv","ok":true}` (uptime checks) |
| other  | any         | `404 {"error":"not_found"}` — EVO falls back to its embedded payload |

## Notes

- Render free tier sleeps after ~15 min idle; first activation after a nap
  takes 30–50 s. Point an uptime pinger at `/health` every 10 min to keep it warm.
- `expiresAt` is year 2100 — the lease counter effectively never runs out.
- `render.yaml` ships the blueprint; `evo_licsrv.py` binds `0.0.0.0:$PORT`
  automatically when `PORT` is set (Render), else `127.0.0.1:8007`.
