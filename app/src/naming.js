const INVALID = /[<>:"/\\|?*\x00-\x1f]/g;
const SEPS = /[\s\-_]+/g;

export function cleanToken(value = "") {
  return String(value).trim().replace(INVALID, "_").replace(SEPS, "_").replace(/^[ ._]+|[ ._]+$/g, "");
}

export function buildHrtFilename({
  domain,
  documentType,
  projectName,
  scope,
  revision,
  extension = "docx",
  userFilename,
}) {
  if (userFilename) {
    const raw = String(userFilename).trim();
    const dot = raw.lastIndexOf(".");
    const stem = cleanToken(dot > 0 ? raw.slice(0, dot) : raw);
    const ext = cleanToken(dot > 0 ? raw.slice(dot + 1) : extension).toLowerCase() || "docx";
    if (!stem) throw new Error("User filename has no usable basename.");
    return `${stem}.${ext}`;
  }
  const d = cleanToken(domain);
  const t = cleanToken(documentType);
  const p = cleanToken(projectName);
  if (!d || !t || !p) throw new Error("domain, documentType and projectName are required.");
  const parts = ["HRT", d, t, p];
  const s = cleanToken(scope || "");
  const r = cleanToken(revision || "");
  if (s) parts.push(s);
  if (r) parts.push(r);
  const ext = cleanToken(extension).toLowerCase() || "docx";
  return `${parts.join("_")}.${ext}`;
}
