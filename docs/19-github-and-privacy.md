# GitHub publication and privacy review

Date: **24 October 2026**. Repository requested: **RicoMitra/Kai**, **private**. The owner explicitly requested a detailed description and asked that their local privacy guidance be read before publication. That private file is not copied into the repository.

## Publication boundary

The project originally inherited a Git repository rooted at the Windows user directory with a placeholder remote. Kai now has its own nested, project-root `.git` directory and fresh project-only history. The parent repository, remote, history and global Git identity are not changed or imported.

The local working branch is `codex/initial-publish`; the initial publication targets GitHub `main`. Commits use the owner's GitHub noreply address rather than the personal email from an inherited Git configuration. The remote uses an ordinary credential-free HTTPS URL; authentication remains in the existing GitHub CLI credential store.

Committed material includes active/archival source modules, launcher/source, identity assets, Markdown documentation, selected generated-fixture screenshots and evidence. `.gitignore` excludes local runtime/model/cache/data files, credentials, logs, original owner ZIP archives, reference photos and generated release ZIPs. These local materials are preserved on disk; exclusion does not delete or rewrite them.

Some historical development documents intentionally retain workstation paths and descriptions of private local references. Keep the repository private unless those documents and image rights are reviewed again. A source ZIP generated locally can include local design references through its own allowlist; do not assume that archive has the same boundary as Git staging.

## Applying the owner's privacy checklist

| Requirement | Application to Kai | Outcome / remaining work |
| --- | --- | --- |
| Hide API keys; purge Git secrets | Keep environment/settings/OAuth files out of commits; inspect staged content/history | Fresh project-only history; redacted Gitleaks scan is required before push. If a real credential is found, revoke/rotate it as well as removing it |
| Public DB key; row-level security; server-side auth; record access | Kai has no remote DB API or multi-user account backend | Not applicable to the current local SQLite architecture; do not claim these controls exist |
| Encrypt sensitive data | Notes, clipboard history and OAuth material are local files | **Not implemented at application level.** Repository exclusion prevents upload, not local-account access. Encryption/migration/recovery remains a separate engineering task |
| Session cookies; password hashing; login rate limits; bots | No application web login/password store | Not applicable to Kai's present desktop UI. Spotify delegates authorization to its provider using PKCE |
| Parameterized queries | User values enter SQLite operations | Source uses bound SQL parameters; schema/query fragments are controlled application code |
| Validate input; escape content; block field tampering | File conversions, notes/clipboard bounds, browser URLs, generated Word/Qt markup | Format/direction/size/page/text checks, escaped document text, internal IDs and local process boundary; no claim of an OS-level hostile-file sandbox |
| Restrict uploads | There is no public upload endpoint | Local conversion restricts supported formats and counts; Shelf can reference arbitrary local file types without auto-executing them |
| Trim responses | External services only where used | Lyrics/service responses and disk cache are bounded; conversion returns result paths rather than transferring full rendered images to the GUI |
| Security headers; force HTTPS | No public HTTP application | External service URLs use HTTPS; Spotify's loopback callback is local HTTP by design, not a hosted public endpoint |
| Scan dependencies | Direct requirements and their installed active dependency closure | pip-audit applied; HTTP/TLS findings remediated and versions pinned; native/transitive license/security scope remains limited |

This is a publication review and an honest statement of current application controls. It is not a claim that every item in a general web-application security checklist has been implemented.

## Dependency audit

Tools run in an external development cache, not as Kai production dependencies. **pip-audit 2.10.1** checked the installed active requirements closure: **26 packages**, with no missing metadata during export. The initial scan reported 21 finding entries in four older dependencies; some advisory identifiers were repeated by the advisory feed.

The following updates were installed **inside Kai's isolated runtime**, leaving the older copies in the global Python environment unchanged, and explicitly pinned in `kai/requirements.txt`:

| Package | Previous resolved version | Security-pinned version | License metadata |
| --- | --- | --- | --- |
| requests | 2.32.3 | 2.33.0 | Apache-2.0 |
| urllib3 | 2.3.0 | 2.8.0 | MIT |
| idna | 3.10 | 3.15 | BSD-3-Clause |
| certifi | 2025.1.31 | 2026.10.19 | MPL-2.0 |

The repeated active-closure audit reported **no known vulnerabilities in the 26 scanned Python packages**, with no skipped packages. This does not audit native Qt/PDFium binaries or Windows components. Historical speech packages present elsewhere are not silently treated as active Kai dependencies. Evidence: [dependency-audit-verification.json](../artifacts/productivity/dependency-audit-verification.json).

Reproduce the closure without auditing unrelated global packages:

```powershell
$kaiPython = "$env:LOCALAPPDATA\Kai\runtime\Scripts\python.exe"
$kaiAuditRequirements = Join-Path $env:TEMP 'kai-active-audit-requirements.txt'
& $kaiPython -B tools/export_active_dependencies.py --output $kaiAuditRequirements
uvx --from pip-audit pip-audit -r $kaiAuditRequirements --no-deps --disable-pip
```

Use an isolated development tool installation if uvx is unavailable; do not add the scanner to production requirements. Package names/versions are queried against the advisory service; private documents, notes and tokens are not submitted. Weekly Dependabot configuration is in `.github/dependabot.yml`. Known-advisory results are dated evidence, not a guarantee about future disclosures or every input.

## Secret scanning

Gitleaks **8.30.1** is downloaded from its official release into the temporary audit directory and its archive SHA-256 is checked against that release's checksum file. Staged files and fresh Git history are scanned with **redaction enabled**; reports remain outside the source tree. No secret values are copied into this document.

The staged secret scan returned zero findings after removing a code-expression false positive by formatting the conditional clearly; no detector suppression was added. The final full-history scan and remote commit are verified before reporting publication complete. GitHub repository visibility is PRIVATE, vulnerability alerts and automated security fixes are enabled, and weekly Dependabot checks are configured. Recheck before every later publish, especially if screenshots, credentials, copied documents or a source ZIP have changed.

## Documentation and reviewable evidence

- `README.md` is generated from `docs/readme-source.md` by `tools/build_readme.py` and explains the current product in English.
- `SECURITY.md` describes local storage, network boundaries, exclusions and encryption limitations.
- `docs/history/README-before-github.md` preserves the preceding README, explicitly as development history.
- `handoff.md` is regenerated from `docs/handoff-source.md` with all Markdown headings and the project inventory.
- Unit and relevant GUI/conversion checks are rerun after the dependency security pins. Account playback/login are not mutated in those tests.
- The strict **50 MiB whole-process ceiling remains unachieved/unproven**; publication must not describe Kai as guaranteed to stay under it.

Primary tool references: [Gitleaks](https://github.com/gitleaks/gitleaks), [pip-audit](https://github.com/pypa/pip-audit), and the version-specific [requests](https://pypi.org/project/requests/2.33.0/), [urllib3](https://pypi.org/project/urllib3/2.8.0/), [idna](https://pypi.org/project/idna/3.15/), [certifi](https://pypi.org/project/certifi/2026.10.19/) package metadata.
