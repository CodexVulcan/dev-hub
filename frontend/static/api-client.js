/**
 * api-client.js - DevHub typed API client
 * Depends on app.js being loaded first (provides window.apiFetch).
 */

const ApiClient = (() => {

  const teams = {
    list:       ()        => apiFetch("/api/teams/members"),
    create:     (body)    => apiFetch("/api/teams/members",          { method:"POST",  body }),
    updateRole: (id,body) => apiFetch(`/api/teams/members/${id}/role`,{ method:"PATCH", body }),
    remove:     (id)      => apiFetch(`/api/teams/members/${id}`,    { method:"DELETE" }),
  };

  const pipeline = {
    list:        ()           => apiFetch("/api/pipeline/projects"),
    create:      (body)       => apiFetch("/api/pipeline/projects",              { method:"POST",  body }),
    updateStage: (id,body)    => apiFetch(`/api/pipeline/projects/${id}/stage`,  { method:"PATCH", body }),
    githubSync:  (id,own,rep) => apiFetch(`/api/pipeline/projects/${id}/github-sync?owner=${encodeURIComponent(own)}&repo=${encodeURIComponent(rep)}`),
  };

  const mindmap = {
    get:        ()       => apiFetch("/api/mindmap"),
    addNode:    (body)   => apiFetch("/api/mindmap/nodes", { method:"POST", body }),
    addEdge:    (body)   => apiFetch("/api/mindmap/edges", { method:"POST", body }),
    updateNode: (id,opts={}) => {
      const p = new URLSearchParams();
      if (opts.x     !== undefined) p.set("x",     opts.x);
      if (opts.y     !== undefined) p.set("y",     opts.y);
      if (opts.label !== undefined) p.set("label", opts.label);
      return apiFetch(`/api/mindmap/nodes/${id}?${p}`, { method:"PATCH" });
    },
    removeNode: (id) => apiFetch(`/api/mindmap/nodes/${id}`, { method:"DELETE" }),
  };

  const dashboard = {
    list:       ()        => apiFetch("/api/dashboard/cards"),
    create:     (body)    => apiFetch("/api/dashboard/cards",             { method:"POST",   body }),
    update:     (id,body) => apiFetch(`/api/dashboard/cards/${id}`,       { method:"PATCH",  body }),
    remove:     (id)      => apiFetch(`/api/dashboard/cards/${id}`,       { method:"DELETE" }),
    addComment: (id,body) => apiFetch(`/api/dashboard/cards/${id}/comments`,{ method:"POST", body }),
  };

  const analyzer = {
    analyze: (body) => apiFetch("/api/analyzer/analyze", { method:"POST", body }),
  };

  const debugging = {
    create:  (body) => apiFetch("/api/debugging/report",          { method:"POST",  body }),
    list:    ()     => apiFetch("/api/debugging/reports"),
    get:     (id)   => apiFetch(`/api/debugging/reports/${id}`),
    resolve: (id)   => apiFetch(`/api/debugging/issues/${id}/resolve`, { method:"PATCH" }),
  };

  const review = {
    summarize: (body) => apiFetch("/api/review/summarize", { method:"POST", body }),
    history:   ()     => apiFetch("/api/review/history"),
  };

  const testing = {
    submit: (body) => apiFetch("/api/testing/results", { method:"POST", body }),
    list:   ()     => apiFetch("/api/testing/reports"),
    get:    (id)   => apiFetch(`/api/testing/reports/${id}`),
  };

  const deployment = {
    check: (projectId) => apiFetch(`/api/deployment/check/${projectId}`),
  };

  const maintenance = {
    list:   ()        => apiFetch("/api/maintenance/tasks"),
    create: (body)    => apiFetch("/api/maintenance/tasks",    { method:"POST",   body }),
    update: (id,body) => apiFetch(`/api/maintenance/tasks/${id}`,{ method:"PATCH", body }),
    remove: (id)      => apiFetch(`/api/maintenance/tasks/${id}`,{ method:"DELETE" }),
  };

  const pulse = {
    score: () => apiFetch("/api/pulse/score"),
    feed:  () => apiFetch("/api/pulse/feed"),
    all:   () => apiFetch("/api/pulse"),
  };

  const system = {
    health: () => apiFetch("/api/health"),
    export: () => apiFetch("/api/export"),
  };

  return { teams, pipeline, mindmap, dashboard, analyzer, debugging, review, testing, deployment, maintenance, pulse, system };
})();

window.ApiClient = ApiClient;