# Claude Code Security review gate

Claude Code Security is a separate Anthropic service/feature, not an automatic protection gained by adding a dependency or a YAML file. Access, pricing, availability and GitHub integration must be verified in the owner's Anthropic account before enabling it. No API key, subscription, billing, or third-party repository access is authorized by this file.

## Review policy for Hermes upstream

- Treat downloaded Hermes source, dependencies, tool descriptions and agent outputs as untrusted until reviewed.
- Pin upstream to a reviewed commit SHA; verify the recorded SHA and review dependency changes before installing.
- Run dependency and secret scanning in CI; use GitHub code scanning / Dependabot where available.
- If Claude Code Security becomes available, connect it with least-privilege repository permissions, scope to this repo, and require owner approval before sending private source to any external service or enabling charges.
- Do not allow untrusted upstream scripts to inherit API keys, GitHub tokens, cloud credentials, or publishing secrets.
- Restrict Hermes runtime tools to approved executables and network destinations; do not grant arbitrary shell or publishing access to content inputs.
- Preserve owner-only RELEASE_APPROVED gate; security scan passing is never authorization to publish.

## Status

Policy added only. **Claude Code Security is not connected or running.** No scan results are claimed.
