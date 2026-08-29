"""
analyzer.py — Analyzer module router.
Pure rule-based stack detection + tool suggestions. No filesystem reads.
"""
from fastapi import APIRouter
from backend.schemas.analyzer import AnalyzeRequest, AnalyzeResponse, ToolSuggestion

router = APIRouter(prefix="/api/analyzer", tags=["analyzer"])

# -- Detection rules --------------------------------------------------------
_STACK_RULES = [
    (["requirements.txt", "setup.py", "pyproject.toml", ".py"], "Python"),
    (["package.json", "node_modules", ".js", ".ts", ".tsx"], "Node.js / JavaScript"),
    (["pom.xml", "build.gradle", ".java"], "Java"),
    (["go.mod", "go.sum", ".go"], "Go"),
    (["Cargo.toml", ".rs"], "Rust"),
    (["*.rb", "Gemfile", "Rakefile"], "Ruby"),
    (["composer.json", ".php"], "PHP"),
    (["*.cs", ".csproj", ".sln"], "C# / .NET"),
    (["Dockerfile", "docker-compose.yml", "docker-compose.yaml"], "Docker"),
    (["kubernetes", ".yaml", "helm"], "Kubernetes / Helm"),
    ([".github/workflows", ".circleci", "Jenkinsfile", ".gitlab-ci"], "CI/CD"),
    (["terraform", ".tf"], "Terraform / IaC"),
    (["fastapi", "django", "flask"], "Python Web Framework"),
    (["react", "vue", "angular", "svelte"], "Frontend Framework"),
    (["postgresql", "mysql", "sqlite", "mongodb", "redis"], "Database"),
]

_CONVENTION_RULES = [
    (["tests/", "test_", "_test.py", "spec.js", "__tests__"], "Test directory detected — testing convention present"),
    ([".eslintrc", ".flake8", "ruff.toml", ".rubocop"], "Linter config detected — code style enforced"),
    ([".pre-commit-config.yaml"], "Pre-commit hooks configured"),
    (["Makefile"], "Makefile present — standardised build commands"),
    (["README.md", "README.rst"], "README present"),
    ([".env.example", ".env.sample"], ".env template present — env var convention followed"),
    (["CHANGELOG", "CHANGELOG.md"], "Changelog maintained"),
    (["migrations/", "alembic.ini"], "Database migrations present"),
]

_TOOL_SUGGESTIONS = {
    "Python": {
        "linting":         (["Ruff", "Flake8", "Black", "isort"], "Standard Python linting & formatting tools"),
        "testing":         (["pytest", "pytest-cov", "factory-boy"], "Industry-standard Python testing stack"),
        "ci_cd":           (["GitHub Actions", "pre-commit"], "Lightweight CI for Python projects"),
        "monitoring":      (["Sentry", "Prometheus + prometheus-client"], "Error tracking + metrics"),
        "containerization":(["Docker", "docker-compose"], "Containerise the FastAPI/Python app"),
        "documentation":   (["MkDocs", "Sphinx"], "Auto-generate API docs from docstrings"),
    },
    "Node.js / JavaScript": {
        "linting":         (["ESLint", "Prettier"], "Standard JS/TS linting and formatting"),
        "testing":         (["Jest", "Vitest", "Supertest"], "Fast unit + integration testing for Node"),
        "ci_cd":           (["GitHub Actions", "Husky"], "CI + git hooks for Node projects"),
        "monitoring":      (["Sentry", "Datadog APM"], "Error and performance monitoring"),
        "containerization":(["Docker", "docker-compose"], "Containerise Node apps"),
        "documentation":   (["JSDoc", "TypeDoc"], "API docs from source comments"),
    },
    "Docker": {
        "containerization":(["Docker Scout", "Hadolint"], "Image scanning and Dockerfile linting"),
        "ci_cd":           (["GitHub Actions (docker/build-push-action)"], "Automated image build and push"),
    },
    "CI/CD": {
        "ci_cd":           (["GitHub Actions", "pre-commit", "semantic-release"], "Full CI/CD pipeline tooling"),
    },
}

_DEFAULT_TOOLS = {
    "linting":         (["EditorConfig", "pre-commit"], "Baseline code style tools for any project"),
    "testing":         (["Postman / Bruno"], "API contract testing"),
    "ci_cd":           (["GitHub Actions"], "General-purpose CI/CD"),
    "monitoring":      (["UptimeRobot", "Sentry"], "Basic uptime + error monitoring"),
    "containerization":(["Docker"], "Containerisation baseline"),
    "documentation":   (["Docusaurus", "Swagger / OpenAPI"], "Project and API documentation"),
}


def _detect(file_listing: str, tech_hints: str) -> dict:
    text = (file_listing + "\n" + tech_hints).lower()

    stack = []
    for keywords, label in _STACK_RULES:
        if any(kw.lower() in text for kw in keywords):
            if label not in stack:
                stack.append(label)

    conventions = []
    for keywords, label in _CONVENTION_RULES:
        if any(kw.lower() in text for kw in keywords):
            conventions.append(label)

    tool_map: dict[str, tuple] = dict(_DEFAULT_TOOLS)
    for stack_label, categories in _TOOL_SUGGESTIONS.items():
        if stack_label in stack:
            for cat, val in categories.items():
                tool_map[cat] = val

    suggestions = [
        ToolSuggestion(category=cat, tools=tools, reason=reason)
        for cat, (tools, reason) in tool_map.items()
    ]

    return {
        "stack_summary": stack or ["Unknown — no recognisable files detected"],
        "conventions": conventions or ["No established conventions detected"],
        "tool_suggestions": suggestions,
    }


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(body: AnalyzeRequest):
    """
    Accepts { file_listing, tech_hints } — plain text only.
    Never reads files from the filesystem.
    """
    return _detect(body.file_listing, body.tech_hints)
