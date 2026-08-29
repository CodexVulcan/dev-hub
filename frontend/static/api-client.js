/**
 * api-client.js � DevHub typed API client
 *
 * Every module exposes named async methods that map 1-to-1 with backend
 * endpoints. Pages call ApiClient.teams.list() instead of raw apiFetch().
 *
 * Depends on app.js being loaded first (provides window.apiFetch).
 */

const ApiClient = (() => {

  // -- Teams -------------------------------------------------------------
  const teams = {
    /** GET /api/teams/members ? { members: MemberResponse[] } */
    list: () => apiFetch("/api/teams/members"),

    /**
     * POST /api/teams/members
     * @param {{ name: string, email: string, role: string }} body
     */
    create: (body) => apiFetch("/api/teams/members", { method: "POST", body }),

    /**
     * PATCH /api/teams/members/:id/role
     * @param {number} id
     * @param {{ role: string }} body
     */
    updateRole: (id, body) =>
      apiFetch(`/api/teams/members/${id}/role`, { method: "PATCH", body }),

    /** DELETE /api/teams/members/:id */
    remove: (id) => apiFetch(`/api/teams/members/${id}`, { method: "DELETE" }),
  };

  // -- Pipeline ----------------------------------------------------------
  const pipeline = {
    /** GET /api/pipeline/projects ? { projects: ProjectResponse[] } */
    list: () => apiFetch("/api/pipeline/projects"),

    /**
     * POST /api/pipeline/projects
     * @param {{ name: string, description?: string, github_owner?: string, github_repo?: string }} body
     */
    create: (body) => apiFetch("/api/pipeline/projects", { method: "POST", body }),

    /**
     * PATCH /api/pipeline/projects/:id/stage
     * @param {number} id
     * @param {{ stage: string, status: string }} body
     */
    updateStage: (id, body) =>
      apiFetch(`/api/pipeline/projects/${id}/stage`, { method: "PATCH", body }),

    /**
     * GET /api/pipeline/projects/:id/github-sync?owner=&repo=
     * Fetches latest GitHub Actions status for the project.
     * Token is env-only on server � never passed from frontend.
     * @param {number} id
     * @param {string} owner
     * @param {string} repo
     */
    githubSync: (id, owner, repo) =>
      apiFetch(`/api/pipeline/projects/${id}/github-sync?owner=${encodeURIComponent(owner)}&repo=${encodeURIComponent(repo)}`),
  };

  // -- Mindmap -----------------------------------------------------------
  const mindmap = {
    /** GET /api/mindmap ? { nodes, edges } */
    get: () => apiFetch("/api/mindmap"),

    /** POST /api/mindmap/nodes */
    addNode: (body) => apiFetch("/api/mindmap/nodes", { method: "POST", body }),

    /** POST /api/mindmap/edges */
    addEdge: (body) => apiFetch("/api/mindmap/edges", { method: "POST", body }),

    /**
     * PATCH /api/mindmap/nodes/:id -- update x/y position or label
     * @param {string} id
     * @param {{ x?: number, y?: number, label?: string }} opts
     */
    updateNode: (id, opts = {}) => {
      const params = new URLSearchParams();
      if (opts.x !== undefined) params.set("x", opts.x);
      if (opts.y !== undefined) params.set("y", opts.y);
      if (opts.label !== undefined) params.set("label", opts.label);
      return apiFetch(`/api/mindmap/nodes/${id}?${params}`, { method: "PATCH" });
    },

    /** DELETE /api/mindmap/nodes/:id */
    removeNode: (id) => apiFetch(`/api/mindmap/nodes/${id}`, { method: "DELETE" }),
  };

  // -- Dashboard ---------------------------------------------------------
  const dashboard = {
    /** GET /api/dashboard/cards */
    list: () => apiFetch("/api/dashboard/cards"),

    /** POST /api/dashboard/cards */
    create: (body) => apiFetch("/api/dashboard/cards", { method: "POST", body }),

    /** PATCH /api/dashboard/cards/:id */
    update: (id, body) =>
      apiFetch(`/api/dashboard/cards/${id}`, { method: "PATCH", body }),

    /** DELETE /api/dashboard/cards/:id */
    remove: (id) => apiFetch(`/api/dashboard/cards/${id}`, { method: "DELETE" }),

    /** POST /api/dashboard/cards/:id/comments */
    addComment: (id, body) =>
      apiFetch(`/api/dashboard/cards/${id}/comments`, { method: "POST", body }),
  };

  // -- Analyzer ----------------------------------------------------------
  const analyzer = {
    /**
     * POST /api/analyzer/analyze
     * @param {{ file_listing: string, tech_hints?: string }} body
     */
    analyze: (body) => apiFetch("/api/analyzer/analyze", { method: "POST", body }),
  };

  // -- Debugging ---------------------------------------------------------
  const debugging = {
    /** POST /api/debugging/report */
    create: (body) => apiFetch("/api/debugging/report", { method: "POST", body }),

    /** GET /api/debugging/reports */
    list: () => apiFetch("/api/debugging/reports"),

    /** GET /api/debugging/reports/:id */
    get: (id) => apiFetch(`/api/debugging/reports/${id}`),
  };

  // -- Review ------------------------------------------------------------
  const review = {
    /**
     * POST /api/review/summarize
     * @param {{ changes_text: string }} body
     */
    summarize: (body) => apiFetch("/api/review/summarize", { method: "POST", body }),

    /** GET /api/review/history */
    history: () => apiFetch("/api/review/history"),
  };

  // -- Testing -----------------------------------------------------------
  const testing = {
    /**
     * POST /api/testing/results
     * @param {{ test_suite: string, results: TestResultInput[] }} body
     */
    submit: (body) => apiFetch("/api/testing/results", { method: "POST", body }),

    /** GET /api/testing/reports */
    list: () => apiFetch("/api/testing/reports"),

    /** GET /api/testing/reports/:id */
    get: (id) => apiFetch(`/api/testing/reports/${id}`),
  };

  // -- Deployment --------------------------------------------------------
  const deployment = {
    /**
     * GET /api/deployment/check/:projectId
     * @param {number} projectId
     */
    check: (projectId) => apiFetch(`/api/deployment/check/${projectId}`),
  };

  // -- Maintenance -------------------------------------------------------
  const maintenance = {
    /** GET /api/maintenance/tasks */
    list: () => apiFetch("/api/maintenance/tasks"),

    /** POST /api/maintenance/tasks */
    create: (body) => apiFetch("/api/maintenance/tasks", { method: "POST", body }),

    /**
     * PATCH /api/maintenance/tasks/:id
     * @param {number} id
     * @param {{ status?: string, due_date?: string }} body
     */
    update: (id, body) =>
      apiFetch(`/api/maintenance/tasks/${id}`, { method: "PATCH", body }),

    /** DELETE /api/maintenance/tasks/:id */
    remove: (id) => apiFetch(`/api/maintenance/tasks/${id}`, { method: "DELETE" }),
  };

  // -- System ------------------------------------------------------------
  const system = {
    /** GET /api/health */
    health: () => apiFetch("/api/health"),

    /** GET /api/export � full platform state snapshot */
    export: () => apiFetch("/api/export"),
  };

  return { teams, pipeline, mindmap, dashboard, analyzer, debugging, review, testing, deployment, maintenance, pulse, system };
})();

window.ApiClient = ApiClient;
