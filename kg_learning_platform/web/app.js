const state = {
  documents: [],
  selectedDocumentId: null,
  selectedDetail: null,
  parserBackends: [],
  activeTab: "overview",
  chunkFilter: "all",
  activeAssetPath: null,
  assetPreview: null,
};

const CHUNK_LABELS = {
  all: "全部",
  concept: "概念",
  formula: "公式",
  image: "图片",
  table: "表格",
  example: "例题",
  proof: "证明",
};

const ASSET_LABELS = {
  image: "图片",
  markdown: "Markdown",
  json: "JSON",
  pdf: "PDF",
  archive: "压缩包",
  file: "文件",
};

const $ = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json();
}

function setHealth(ok, text) {
  $("health-dot").className = `dot ${ok ? "ok" : "bad"}`;
  $("health-text").textContent = text;
}

async function loadHealth() {
  try {
    const health = await api("/api/health");
    setHealth(true, `${health.documents} 文档 · ${health.chunks} chunks · ${health.graph_nodes} 节点`);
  } catch (error) {
    setHealth(false, `服务异常：${error.message}`);
  }
}

async function loadParserBackends() {
  state.parserBackends = await api("/api/parser/backends");
}

async function loadDocuments() {
  state.documents = await api("/api/documents");
  if (!state.selectedDocumentId && state.documents.length) {
    state.selectedDocumentId = state.documents[0].id;
  }
  if (state.selectedDocumentId && !state.documents.some((doc) => doc.id === state.selectedDocumentId)) {
    state.selectedDocumentId = state.documents[0]?.id || null;
  }
  renderDocuments();
  if (state.selectedDocumentId) {
    await loadDocumentDetail(state.selectedDocumentId);
  } else {
    state.selectedDetail = null;
    renderDetail();
  }
}

function renderDocuments() {
  const container = $("documents-list");
  if (!state.documents.length) {
    container.innerHTML = '<div class="muted-box">暂无资料。上传 PDF、课件或论文后即可开始构建知识库。</div>';
    return;
  }
  container.innerHTML = state.documents.map(renderDocumentCard).join("");
}

function renderDocumentCard(doc) {
  const quality = doc.metadata?.parse_quality;
  const score = quality?.quality_score ?? "-";
  const title = decodeMojibake(doc.title || doc.filename);
  const parser = doc.metadata?.parser_backend || doc.metadata?.parser || "未解析";
  const active = doc.id === state.selectedDocumentId ? "active" : "";
  const cache = doc.metadata?.parser_cache_hit ? "缓存" : "新解析";
  const status = doc.status || "uploaded";
  return `
    <button type="button" class="document-card ${active}" data-document-id="${escapeAttr(doc.id)}">
      <span class="doc-title">${escapeHtml(title)}</span>
      <span class="doc-meta">${escapeHtml(doc.content_type || "unknown")} · ${escapeHtml(parser)} · ${escapeHtml(status)}</span>
      <span class="doc-footer">
        <span class="${qualityBadgeClass(score)}">质量 ${escapeHtml(score)}</span>
        <span>${quality?.formula_count ?? 0} 公式</span>
        <span>${quality?.table_count ?? 0} 表格</span>
        <span>${cache}</span>
      </span>
    </button>
  `;
}

async function selectDocument(id) {
  if (!id || id === state.selectedDocumentId) return;
  state.selectedDocumentId = id;
  state.chunkFilter = "all";
  state.activeTab = "overview";
  state.activeAssetPath = null;
  state.assetPreview = null;
  renderDocuments();
  await loadDocumentDetail(id);
}

async function loadDocumentDetail(id) {
  state.selectedDetail = await api(`/api/documents/${encodeURIComponent(id)}/detail`);
  renderDetail();
}

function renderDetail() {
  const detail = state.selectedDetail;
  const doc = detail?.document;
  $("detail-title").textContent = doc ? decodeMojibake(doc.title || doc.filename) : "选择一份资料";
  const enabled = Boolean(doc);
  const mineruConfigured = hasBackend("mineru-precision") && hasBackendToken("mineru-precision");
  const precisionReady = mineruConfigured || hasMineruPrecisionCache(doc);
  $("detail-parse-basic").disabled = !enabled;
  $("detail-parse-mineru").disabled = !enabled || !hasBackend("mineru-precision") || !precisionReady;
  $("detail-parse-mineru").title = precisionReady ? "使用 MinerU 精准结果或本地缓存" : "需要配置 MINERU_API_TOKEN，或先有可复用的 MinerU 缓存";
  $("detail-force-mineru").disabled = !enabled || !mineruConfigured;
  $("detail-force-mineru").title = mineruConfigured ? "忽略缓存并重新调用 MinerU" : "需要在服务环境配置 MINERU_API_TOKEN";
  renderQualityGrid(doc?.metadata?.parse_quality, detail);
  renderActiveTab();
}

function renderQualityGrid(quality, detail) {
  const grid = $("quality-grid");
  if (!quality) {
    grid.innerHTML = `
      <div class="metric-card"><span>质量</span><strong>-</strong><small>尚未解析</small></div>
      <div class="metric-card"><span>Chunks</span><strong>${detail?.chunk_count ?? 0}</strong><small>等待解析</small></div>
    `;
    return;
  }
  grid.innerHTML = [
    metric("质量", quality.quality_score, qualityHint(quality.quality_score), qualityBadgeClass(quality.quality_score)),
    metric("公式", quality.formula_count, `${quality.formula_block_count || 0} 块公式`),
    metric("表格", quality.table_count, `${quality.html_table_count || 0} HTML 表格`),
    metric("图片", quality.markdown_image_count, `${detail?.assets?.length ?? 0} 个资产文件`),
    metric("Chunks", quality.chunk_count, chunkTypeSummary(detail?.chunk_type_counts || {})),
    metric("缓存", detail?.document?.metadata?.parser_cache_hit ? "命中" : "未命中", "精准解析优先复用 full.md"),
  ].join("");
}

function metric(label, value, hint, tone = "") {
  return `
    <div class="metric-card ${tone}">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value ?? "-")}</strong>
      <small>${escapeHtml(hint || "")}</small>
    </div>
  `;
}

function qualityHint(score) {
  if (score >= 85) return "解析质量稳定";
  if (score >= 65) return "可用，建议抽查";
  return "建议重跑或人工检查";
}

function qualityBadgeClass(score) {
  const numeric = Number(score);
  if (Number.isNaN(numeric)) return "tone-neutral";
  if (numeric >= 85) return "tone-good";
  if (numeric >= 65) return "tone-warn";
  return "tone-bad";
}

function chunkTypeSummary(counts) {
  const entries = Object.entries(counts);
  return entries.length
    ? entries.map(([key, value]) => `${CHUNK_LABELS[key] || key}:${value}`).join(" · ")
    : "暂无类型统计";
}

function renderActiveTab() {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.tab === state.activeTab);
  });
  const detail = state.selectedDetail;
  const content = $("detail-content");
  if (!detail) {
    content.innerHTML = '<div class="muted-box">选择文档后可查看详情。</div>';
    return;
  }
  if (state.activeTab === "overview") {
    content.innerHTML = renderOverview(detail);
  }
  if (state.activeTab === "chunks") {
    content.innerHTML = renderChunksTab(detail);
    loadChunks(state.selectedDocumentId, state.chunkFilter).catch(showInlineError);
  }
  if (state.activeTab === "assets") {
    content.innerHTML = renderAssetsTab(detail);
    ensureAssetPreviewLoaded().catch(showInlineError);
  }
  if (state.activeTab === "markdown") {
    content.innerHTML = renderMarkdownTab(detail);
  }
  if (state.activeTab === "history") {
    content.innerHTML = renderHistoryTab(detail);
  }
}

function renderOverview(detail) {
  const doc = detail.document;
  const metadata = doc.metadata || {};
  const quality = metadata.parse_quality || {};
  const parsedAt = doc.parsed_at ? formatDate(doc.parsed_at) : "尚未解析";
  return `
    <div class="overview-grid">
      <div class="info-block">
        <span>解析器</span>
        <strong>${escapeHtml(metadata.parser_backend || metadata.parser || "未解析")}</strong>
        <small>${metadata.parser_cache_hit ? "已命中本地缓存" : "最近一次为新解析"}</small>
      </div>
      <div class="info-block">
        <span>解析资产</span>
        <strong>${detail.assets.length}</strong>
        <small>${escapeHtml(metadata.parser_artifact_dir || "暂无资产目录")}</small>
      </div>
      <div class="info-block">
        <span>文本规模</span>
        <strong>${quality.char_count || metadata.char_count || 0}</strong>
        <small>${detail.chunk_count} chunks · ${parsedAt}</small>
      </div>
    </div>
    <div class="quality-strip">
      ${qualityItem("标题", doc.title || doc.filename)}
      ${qualityItem("文件", doc.filename)}
      ${qualityItem("SHA256", metadata.file_sha256 ? `${metadata.file_sha256.slice(0, 16)}...` : "未记录")}
    </div>
    ${metadata.parser_fallback_error ? `<div class="item-warning">${escapeHtml(metadata.parser_fallback_error)}</div>` : ""}
  `;
}

function qualityItem(label, value) {
  return `
    <div class="quality-item">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(decodeMojibake(value || "-"))}</strong>
    </div>
  `;
}

function renderChunksTab(detail) {
  const counts = detail.chunk_type_counts || {};
  const filters = [["all", detail.chunk_count], ...Object.entries(counts)];
  return `
    <div class="chunk-toolbar">
      ${filters.map(([type, count]) => `
        <button type="button" class="chip ${state.chunkFilter === type ? "active" : ""}" data-chunk-filter="${escapeAttr(type)}">
          ${escapeHtml(CHUNK_LABELS[type] || type)} ${escapeHtml(count)}
        </button>
      `).join("")}
    </div>
    <div id="chunks-inline" class="list"><div class="muted-box">正在读取 chunks...</div></div>
  `;
}

function renderAssetsTab(detail) {
  if (!detail.assets.length) {
    state.activeAssetPath = null;
    return '<div class="muted-box">暂无解析资产。使用 MinerU 精准解析后会看到 full.md、图片、JSON 和 zip 文件。</div>';
  }
  const selected = selectedAsset(detail.assets);
  return `
    <div class="asset-browser">
      <div class="asset-list">
        ${detail.assets.slice(0, 120).map((asset) => `
          <button type="button" class="asset-row ${asset.relative_path === selected.relative_path ? "active" : ""}" data-asset-path="${escapeAttr(asset.relative_path)}">
            <span>
              <strong>${escapeHtml(asset.relative_path)}</strong>
              <small>${escapeHtml(ASSET_LABELS[asset.kind] || asset.kind || "文件")} · ${formatBytes(asset.size)}</small>
            </span>
          </button>
        `).join("")}
      </div>
      <div id="asset-preview" class="asset-preview">
        ${renderAssetPreview(selected)}
      </div>
    </div>
  `;
}

function selectedAsset(assets) {
  let asset = assets.find((item) => item.relative_path === state.activeAssetPath);
  if (!asset) asset = assets.find((item) => item.kind === "image") || assets[0];
  state.activeAssetPath = asset.relative_path;
  return asset;
}

function renderAssetPreview(asset) {
  const url = assetUrl(asset.relative_path);
  if (asset.kind === "image") {
    return `
      <div class="asset-preview-head">
        <strong>${escapeHtml(asset.relative_path)}</strong>
        <a href="${url}" target="_blank" rel="noreferrer">打开</a>
      </div>
      <img class="asset-image" src="${url}" alt="${escapeAttr(asset.relative_path)}" />
    `;
  }
  if (isTextAsset(asset)) {
    const preview = state.assetPreview?.path === asset.relative_path ? state.assetPreview.text : "正在读取文本预览...";
    return `
      <div class="asset-preview-head">
        <strong>${escapeHtml(asset.relative_path)}</strong>
        <a href="${url}" target="_blank" rel="noreferrer">打开</a>
      </div>
      <pre class="preview asset-text">${escapeHtml(preview)}</pre>
    `;
  }
  return `
    <div class="asset-preview-head">
      <strong>${escapeHtml(asset.relative_path)}</strong>
      <a href="${url}" target="_blank" rel="noreferrer">下载/打开</a>
    </div>
    <div class="muted-box">该资产类型适合在外部查看：${escapeHtml(ASSET_LABELS[asset.kind] || asset.kind || asset.extension || "文件")}。</div>
  `;
}

function renderMarkdownTab(detail) {
  if (!detail.full_markdown_preview) return '<div class="muted-box">暂无 full.md 预览。</div>';
  const suffix = detail.full_markdown_truncated ? "\n\n...预览已截断，可在资产页打开 full.md 查看完整内容。" : "";
  return `<pre class="preview markdown-preview">${escapeHtml(decodeMojibake(detail.full_markdown_preview) + suffix)}</pre>`;
}

function renderHistoryTab(detail) {
  if (!detail.history.length) return '<div class="muted-box">暂无解析历史。</div>';
  return `
    <div class="history-list">
      ${detail.history.slice().reverse().map((item) => {
        const score = Number(item.quality_score ?? 0);
        return `
          <div class="history-row">
            <div class="history-main">
              <strong>${escapeHtml(item.parser_backend || item.requested_backend || "unknown")}</strong>
              <span>${formatDate(item.parsed_at)}</span>
            </div>
            <div class="score-line"><span style="width: ${Math.max(0, Math.min(100, score))}%"></span></div>
            <small>质量 ${item.quality_score ?? "-"} · ${item.chunk_count ?? 0} chunks · ${item.formula_count ?? 0} 公式 · ${item.cache_hit ? "缓存" : "新解析"}</small>
          </div>
        `;
      }).join("")}
    </div>
  `;
}

async function parseDocument(id, backend = "basic", force = false) {
  if (!id) return;
  const label = backend === "mineru-precision" ? "MinerU 精准" : "本地";
  $("detail-content").innerHTML = `<div class="muted-box">${label}解析中，请稍等...</div>`;
  const result = await api(`/api/documents/${encodeURIComponent(id)}/parse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ backend, fallback_to_basic: true, force }),
  });
  state.selectedDetail = {
    document: result.document,
    chunk_count: result.chunk_count,
    assets: [],
    history: [],
    chunk_type_counts: {},
    full_markdown_preview: "",
  };
  await refreshAll();
  await loadDocumentDetail(id);
}

async function loadChunks(id, chunkType = "all") {
  const query = chunkType && chunkType !== "all" ? `?chunk_type=${encodeURIComponent(chunkType)}` : "";
  const chunks = await api(`/api/documents/${encodeURIComponent(id)}/chunks${query}`);
  const target = $("chunks-inline");
  if (!target) return;
  if (!chunks.length) {
    target.innerHTML = '<div class="muted-box">当前类型暂无 chunks。</div>';
    return;
  }
  target.innerHTML = chunks.map((chunk) => `
    <div class="chunk-card">
      <div class="chunk-head">
        <strong>#${chunk.ordinal} ${escapeHtml(decodeMojibake(chunk.heading || "Document"))}</strong>
        <span>${escapeHtml(CHUNK_LABELS[chunk.chunk_type] || chunk.chunk_type || "concept")}</span>
      </div>
      <div class="chunk-metrics">
        <small>${chunk.metadata?.formula_count ?? 0} 公式</small>
        <small>${chunk.metadata?.image_count ?? 0} 图片</small>
        <small>${chunk.metadata?.table_like ? "含表格" : "文本"}</small>
      </div>
      <p>${escapeHtml(decodeMojibake(chunk.text).slice(0, 720))}</p>
    </div>
  `).join("");
}

async function ensureAssetPreviewLoaded() {
  const detail = state.selectedDetail;
  if (!detail || state.activeTab !== "assets") return;
  const asset = detail.assets.find((item) => item.relative_path === state.activeAssetPath);
  if (!asset || !isTextAsset(asset) || state.assetPreview?.path === asset.relative_path) return;
  const response = await fetch(assetUrl(asset.relative_path));
  if (!response.ok) throw new Error(await response.text());
  const text = await response.text();
  state.assetPreview = { path: asset.relative_path, text: decodeMojibake(text.slice(0, 14000)) };
  const preview = $("asset-preview");
  if (preview && state.activeTab === "assets") {
    preview.innerHTML = renderAssetPreview(asset);
  }
}

function decodeMojibake(value) {
  const text = String(value || "");
  if (!/[ÃÂâäåæçèéïð锟閿]/.test(text)) return text;
  try {
    const bytes = Uint8Array.from([...text].map((char) => char.charCodeAt(0) & 255));
    const decoded = new TextDecoder("utf-8", { fatal: false }).decode(bytes);
    return decoded.includes("�") ? text : decoded;
  } catch {
    return text;
  }
}

async function rebuildIndex() {
  const result = await api("/api/index/rebuild", { method: "POST" });
  setHealth(true, `索引完成：${result.chunk_count} chunks · ${result.node_count} nodes`);
  await Promise.all([loadHealth(), loadGraph()]);
}

async function reprocessAll(backend = "basic") {
  const result = await api("/api/maintenance/reprocess-all", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ clear_artifacts: false, backend, fallback_to_basic: true, force: false }),
  });
  setHealth(true, `完成：${result.parsed_count} 解析 · ${result.skipped?.length || 0} 跳过`);
  await refreshAll();
}

async function search(event) {
  event.preventDefault();
  const query = $("search-query").value.trim();
  if (!query) return;
  const results = await api(`/api/search?q=${encodeURIComponent(query)}&top_k=5`);
  $("search-results").innerHTML = results.length
    ? results.map(renderSearchResult).join("")
    : '<div class="muted-box">没有找到结果。</div>';
}

function renderSearchResult(result) {
  const doc = result.document ? decodeMojibake(result.document.filename) : result.chunk.document_id;
  return `
    <div class="item">
      <div class="item-title">${escapeHtml(doc)} · score ${escapeHtml(result.score)}</div>
      <div class="item-meta">${escapeHtml(decodeMojibake(result.chunk.heading || "Document"))} · ${escapeHtml(CHUNK_LABELS[result.chunk.chunk_type] || result.chunk.chunk_type || "concept")}</div>
      <div>${escapeHtml(decodeMojibake(result.chunk.text).slice(0, 320))}</div>
    </div>
  `;
}

async function chat(event) {
  event.preventDefault();
  const question = $("chat-question").value.trim();
  if (!question) return;
  const result = await api("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, top_k: 5 }),
  });
  $("chat-answer").textContent = decodeMojibake(result.answer || "");
}

async function generateNotebook(event) {
  event.preventDefault();
  const topic = $("notebook-topic").value.trim();
  if (!topic) return;
  const artifact = await api("/api/learning-artifacts/generate-notebook", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      topic,
      source_document_ids: state.selectedDocumentId ? [state.selectedDocumentId] : [],
      difficulty: $("notebook-difficulty").value,
      learning_goal: $("notebook-goal").value,
      include_code: $("notebook-code").checked,
      exercise_count: 3,
      output_format: "ipynb",
    }),
  });
  await loadArtifacts();
  setHealth(true, `Notebook 已生成：${artifact.topic}`);
}

async function loadArtifacts() {
  const artifacts = await api("/api/learning-artifacts");
  $("artifacts-list").innerHTML = artifacts.length
    ? artifacts.map((artifact) => `
        <div class="item">
          <div class="item-title">${escapeHtml(decodeMojibake(artifact.topic))}</div>
          <div class="item-meta">${escapeHtml(artifact.id)} · ${formatDate(artifact.created_at)}</div>
          <div class="item-actions"><a href="/api/learning-artifacts/${encodeURIComponent(artifact.id)}/download"><button type="button">下载</button></a></div>
        </div>
      `).join("")
    : '<div class="muted-box">还没有生成 Notebook。</div>';
}

async function loadGraph() {
  const graph = await api("/api/graph");
  $("graph-summary").textContent = `${graph.nodes.length} 个节点，${graph.edges.length} 条关系`;
  $("graph-list").innerHTML = graph.nodes.length
    ? graph.nodes.slice(0, 12).map((node) => `
      <div class="item compact-item">
        <div class="item-title">${escapeHtml(decodeMojibake(node.label))}</div>
        <div class="item-meta">${escapeHtml(node.type)} · mentions ${escapeHtml(node.mentions)}</div>
      </div>
    `).join("")
    : '<div class="muted-box">暂无图谱节点。请先解析文档并重建索引。</div>';
}

async function upload(event) {
  event.preventDefault();
  const file = $("file-input").files[0];
  if (!file) return;
  const form = new FormData();
  form.append("file", file);
  const document = await api("/api/documents/upload", { method: "POST", body: form });
  $("file-input").value = "";
  state.selectedDocumentId = document.id;
  state.activeTab = "overview";
  await refreshAll();
}

async function refreshAll() {
  await Promise.all([loadHealth(), loadParserBackends(), loadArtifacts(), loadGraph()]);
  await loadDocuments();
}

function hasBackend(id) {
  return state.parserBackends.some((backend) => backend.id === id && backend.available);
}

function hasBackendToken(id) {
  const backend = state.parserBackends.find((item) => item.id === id);
  return !backend?.requires_token || Boolean(backend?.token_configured);
}

function hasMineruPrecisionCache(doc) {
  return Boolean(
    doc?.metadata?.parser_backend === "mineru-precision"
    && doc?.metadata?.mineru_full_md_path
  );
}

function isTextAsset(asset) {
  return asset.kind === "markdown"
    || asset.kind === "json"
    || ["txt", "csv", "log", "yaml", "yml"].includes(asset.extension);
}

function assetUrl(relativePath) {
  const encodedPath = String(relativePath).split("/").map(encodeURIComponent).join("/");
  return `/api/documents/${encodeURIComponent(state.selectedDocumentId)}/assets/${encodedPath}`;
}

function showInlineError(error) {
  const content = $("detail-content");
  if (content) {
    content.insertAdjacentHTML("beforeend", `<div class="item-warning">${escapeHtml(error.message)}</div>`);
  }
}

function formatBytes(value) {
  const numeric = Number(value || 0);
  if (numeric < 1024) return `${numeric} B`;
  if (numeric < 1024 * 1024) return `${Math.round(numeric / 1024)} KB`;
  return `${(numeric / 1024 / 1024).toFixed(1)} MB`;
}

function formatDate(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttr(value) {
  return escapeHtml(value);
}

$("refresh-btn").addEventListener("click", refreshAll);
$("upload-form").addEventListener("submit", upload);
$("rebuild-btn").addEventListener("click", rebuildIndex);
$("reprocess-btn").addEventListener("click", () => reprocessAll("basic"));
$("reprocess-mineru-precision-btn").addEventListener("click", () => reprocessAll("mineru-precision"));
$("detail-parse-basic").addEventListener("click", () => parseDocument(state.selectedDocumentId, "basic"));
$("detail-parse-mineru").addEventListener("click", () => parseDocument(state.selectedDocumentId, "mineru-precision"));
$("detail-force-mineru").addEventListener("click", () => parseDocument(state.selectedDocumentId, "mineru-precision", true));
$("graph-btn").addEventListener("click", loadGraph);
$("search-form").addEventListener("submit", search);
$("chat-form").addEventListener("submit", chat);
$("notebook-form").addEventListener("submit", generateNotebook);

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    state.activeTab = tab.dataset.tab;
    renderActiveTab();
  });
});

document.addEventListener("click", async (event) => {
  const documentButton = event.target.closest("button[data-document-id]");
  if (documentButton) {
    await selectDocument(documentButton.dataset.documentId);
    return;
  }

  const chunkFilter = event.target.closest("button[data-chunk-filter]");
  if (chunkFilter) {
    state.chunkFilter = chunkFilter.dataset.chunkFilter || "all";
    renderActiveTab();
    return;
  }

  const assetButton = event.target.closest("button[data-asset-path]");
  if (assetButton) {
    state.activeAssetPath = assetButton.dataset.assetPath;
    state.assetPreview = null;
    renderActiveTab();
  }
});

refreshAll().catch((error) => setHealth(false, error.message));
