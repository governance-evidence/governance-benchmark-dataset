# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it
responsibly by emailing the maintainer directly rather than opening a public
issue.

**Contact:** Open a private advisory via GitHub's
[Security Advisories](https://github.com/governance-evidence/governance-benchmark-dataset/security/advisories/new)
feature, or email the repository owner.

## Scope

This is a research artifact (benchmark dataset and evaluation harness).
It does not handle user credentials, network services, or sensitive data
at runtime. Security concerns most likely relate to:

- Dependency vulnerabilities (checked via `pip-audit` in CI)
- Malformed input data causing unexpected behavior in loaders
- Secret leakage in committed files (checked via `detect-secrets`)

## Response

We aim to acknowledge reports within 48 hours and provide a fix or
mitigation within 7 days for confirmed vulnerabilities.
