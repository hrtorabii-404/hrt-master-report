# Deploy HRT MCP App

## Docker

```bash
docker build -t hrt-mcp .
docker run --rm -p 3000:3000 -e PORT=3000 hrt-mcp
```

Health check:

```bash
curl http://localhost:3000/health
```

برای ChatGPT باید Endpoint از طریق HTTPS عمومی یا Secure MCP Tunnel قابل دسترس باشد.

## Render

فایل `render.yaml` در ریشه مخزن موجود است. Repository را به Render متصل کنید و Blueprint را Deploy کنید. URL نهایی MCP برابر خواهد بود با:

`https://<service>.onrender.com/mcp`

## Railway

پوشه `app/` دارای `railway.json` و Dockerfile است. پس از Deploy، URL `/mcp` را در Developer Mode ثبت کنید.

## App registration

در ChatGPT Developer Mode:

1. Create custom app
2. Display Name: `HRT Runtime`
3. MCP endpoint: `https://.../mcp`
4. Authentication: None (نسخه داخلی اولیه)
5. Scan Tools
6. Create/Publish مطابق سیاست Workspace
7. شناسه `plugin_asdk_app_...` را بردارید و با `scripts/link_registered_app.py` به Plugin متصل کنید.
