import express from "express";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { z } from "zod";
import { buildHrtFilename } from "./naming.js";
import { HRT_VERSION, PROFILES, WORD_CONTRACT } from "./contracts.js";

function makeServer() {
  const server = new McpServer(
    { name: "hrt", version: HRT_VERSION },
    {
      instructions:
        "HRT is the companion app for HRT Master Report V3.2.4. When the user asks @HRT to create, revise, or audit a report, the bundled hrt-master-report skill controls Word generation and fidelity. Resolve report metadata/profile and the dynamic output filename before final delivery. Do not redesign the approved Golden Master.",
    },
  );

  server.registerTool(
    "validate_hrt_request",
    {
      title: "Validate HRT report request",
      description:
        "Use when the user asks HRT to create, revise, format, or audit a report. Confirms the report profile and required naming metadata before document generation.",
      inputSchema: {
        profile: z.enum(Object.keys(PROFILES)),
        projectName: z.string().min(1),
        documentType: z.string().min(1),
        domain: z.string().min(1),
        scope: z.string().optional(),
        revision: z.string().optional(),
      },
      outputSchema: {
        valid: z.boolean(),
        version: z.string(),
        profileLabel: z.string(),
        missing: z.array(z.string()),
        generationContract: z.record(z.string()),
      },
      annotations: { readOnlyHint: true, openWorldHint: false, destructiveHint: false },
    },
    async ({ profile, projectName, documentType, domain }) => {
      const missing = [];
      if (!projectName?.trim()) missing.push("projectName");
      if (!documentType?.trim()) missing.push("documentType");
      if (!domain?.trim()) missing.push("domain");
      return {
        structuredContent: {
          valid: missing.length === 0,
          version: HRT_VERSION,
          profileLabel: PROFILES[profile],
          missing,
          generationContract: WORD_CONTRACT,
        },
        content: [{ type: "text", text: missing.length ? `Missing: ${missing.join(", ")}` : `HRT ${HRT_VERSION} request is ready.` }],
      };
    },
  );

  server.registerTool(
    "resolve_hrt_output_filename",
    {
      title: "Resolve HRT output filename",
      description:
        "Use before delivering an HRT artifact. Generates the request-aware filename required by HRT Master Report V3.2.4.",
      inputSchema: {
        domain: z.string().min(1),
        documentType: z.string().min(1),
        projectName: z.string().min(1),
        scope: z.string().optional(),
        revision: z.string().optional(),
        extension: z.enum(["docx", "pdf"]).default("docx"),
        userFilename: z.string().optional(),
      },
      outputSchema: { filename: z.string(), basename: z.string(), version: z.string() },
      annotations: { readOnlyHint: true, openWorldHint: false, destructiveHint: false },
    },
    async (args) => {
      const filename = buildHrtFilename(args);
      const basename = filename.replace(/\.[^.]+$/, "");
      return {
        structuredContent: { filename, basename, version: HRT_VERSION },
        content: [{ type: "text", text: filename }],
      };
    },
  );

  server.registerTool(
    "get_hrt_report_contract",
    {
      title: "Get HRT report contract",
      description:
        "Returns the fixed HRT Word fidelity and supported profile contract. Use when planning an HRT document or checking whether a requested formatting change is compatible with the master.",
      inputSchema: { profile: z.enum(Object.keys(PROFILES)).optional() },
      outputSchema: {
        version: z.string(),
        profiles: z.record(z.string()),
        wordContract: z.record(z.string()),
      },
      annotations: { readOnlyHint: true, openWorldHint: false, destructiveHint: false },
    },
    async () => ({
      structuredContent: { version: HRT_VERSION, profiles: PROFILES, wordContract: WORD_CONTRACT },
      content: [{ type: "text", text: "HRT Master Report V3.2.4 contract loaded." }],
    }),
  );
  return server;
}

const app = express();
app.use(express.json({ limit: "1mb" }));
app.get("/health", (_req, res) => res.json({ ok: true, app: "HRT", version: HRT_VERSION }));

app.post("/mcp", async (req, res) => {
  const server = makeServer();
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
  try {
    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  } catch (error) {
    if (!res.headersSent) res.status(500).json({ error: "mcp_error", message: String(error) });
  } finally {
    try { await transport.close(); } catch {}
    try { await server.close(); } catch {}
  }
});

app.get("/mcp", (_req, res) => res.status(405).json({ error: "Use MCP Streamable HTTP POST transport." }));
app.delete("/mcp", (_req, res) => res.status(405).end());

const port = Number(process.env.PORT || 3000);
app.listen(port, () => console.log(`HRT MCP ${HRT_VERSION} listening on :${port}/mcp`));
