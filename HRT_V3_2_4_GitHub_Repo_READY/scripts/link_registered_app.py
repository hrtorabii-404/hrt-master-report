#!/usr/bin/env python3
import json, pathlib, re, sys

if len(sys.argv) != 3:
    print("Usage: link_registered_app.py <repo_root> <plugin_asdk_app_...>", file=sys.stderr)
    raise SystemExit(2)
root = pathlib.Path(sys.argv[1]).resolve()
app_id = sys.argv[2].strip()
if not re.fullmatch(r"plugin_asdk_app_[A-Za-z0-9_-]+", app_id):
    raise SystemExit("Invalid app id; expected plugin_asdk_app_...")
plugin = root / "plugins" / "hrt"
(plugin / ".app.json").write_text(json.dumps({"apps":[{"id":app_id,"required":False}]}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
manifest_path = plugin / ".codex-plugin" / "plugin.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["apps"] = "./.app.json"
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(f"Linked {app_id} to HRT plugin")
