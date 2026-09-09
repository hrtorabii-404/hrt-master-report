# HRT V3.2.4 — GitHub/ChatGPT Plugin Repository

این مخزن دو لایه دارد:

1. **HRT Plugin (Skill-only در مرحله اول)** — برای اینکه HRT در بخش Plugins نصب شود و در Surfaceهای پشتیبانی‌شده با `@HRT` فراخوانی شود.
2. **HRT MCP App (مرحله دوم/اختیاری)** — برای انتقال اجرای قطعی ابزارها و کنترل‌های Runtime به App خارجی.

## مسیر سریع برای رسیدن به @HRT

ابتدا فقط همین مخزن را در GitHub قرار دهید. فایل `.agents/plugins/marketplace.json`، پلاگین `hrt` را از `plugins/hrt` معرفی می‌کند. پلاگین در این مرحله **app dependency ندارد** و فقط Skill تأییدشده HRT V3.2.4 را بسته‌بندی می‌کند.

در ChatGPT Workspace Admin:

`Workspace settings → Plugins → Add → Import marketplace`

- Source: URL ریشه Repository در GitHub
- Path: خالی (چون marketplace در ریشه مخزن است)
- Branch: شاخه اصلی یا خالی برای default branch

بعد از Import، Plugin با Display Name **HRT** باید در Plugins ظاهر شود. Installation policy را روی Available یا Installed بگذارید. سپس در ChatGPT Web در Surface پشتیبانی‌شده تست کنید:

`@HRT کل پروپوزال اوراسیا را تهیه کن.`

## مرحله دوم: اتصال MCP App

اگر Developer Mode / Custom Apps در Workspace شما فعال است، پوشه `app/` یک MCP Server بدون احراز هویت برای تست داخلی دارد:

- Health: `/health`
- MCP: `/mcp`

آن را روی یک HTTPS ثابت Deploy کنید (Docker/Render/Railway قابل استفاده است)، سپس در ChatGPT Developer Mode یک Custom App با Display Name **HRT Runtime** بسازید و MCP URL را ثبت کنید.

پس از دریافت شناسه واقعی `plugin_asdk_app_...` اجرا کنید:

```bash
python scripts/link_registered_app.py . plugin_asdk_app_xxxxxxxxx
```

این اسکریپت `.app.json` واقعی را می‌سازد و `apps: "./.app.json"` را به manifest پلاگین اضافه می‌کند. سپس تغییرات را Commit و Marketplace را Sync/Refresh کنید.

## کنترل قبل از Commit

```bash
python scripts/validate_hrt_repo.py .
```

## نکته مهم

برای `@HRT`، MCP الزامی نیست. طبق ساختار فعلی Plugins، پلاگین می‌تواند فقط Skill داشته باشد. MCP زمانی اضافه می‌شود که بخواهیم Runtime قطعی بیرونی برای ابزارها/عملیات داشته باشیم.
