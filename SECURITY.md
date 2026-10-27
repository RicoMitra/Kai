# Security and privacy

Kai is a local Windows desktop prototype. The GitHub repository is **public** (since 27 October 2026). Public visibility makes the source readable by anyone; it is not a claim that the application is fully hardened.

## Keep personal material out of Git

Never commit `.env` files, API keys, OAuth access/refresh tokens, credentials, SQLite databases, clipboard images, private notes, logs, conversion inputs/results, local settings, runtime environments, or model files. These belong outside the source tree under the local Kai data directory or another user-chosen location.

The initial publication uses fresh project-only Git history rather than importing a parent user-folder repository. Original ZIP archives and owner reference photos remain local. Only selected generated-fixture screenshots and verification reports are included. Use the account's GitHub noreply address for commits when maintaining this privacy boundary.

If a real credential is exposed, revoke/rotate it first. Removing it from the current file or rewriting Git history does not invalidate a leaked credential. Coordinate any history rewrite with the owner; do not rewrite an unrelated parent repository.

## Current protection model

- Clipboard history is event-driven, bounded, pausable and removable. It honors supported password-manager/Windows exclusion hints, but cannot recognize every sensitive item copied by every application.
- Notes, history and Shelf metadata are stored locally. SQL values use parameterized queries; fixed schema migrations use controlled SQL. There is no public database client or multi-user record API.
- Conversion accepts a restricted set of formats/directions with file-size, image, document, page and text limits. It uses a disposable process and owned scratch directories. It is not a hardened operating-system sandbox for hostile documents.
- Extracted Word text is escaped when constructing Qt HTML. DOCX external relationships are not followed. Image members are normalized and restricted to `word/media/`; the entire archive is not extracted into an arbitrary path.
- Browser actions require a click and a validated HTTP/HTTPS URL. Files in Shelf open only through user actions.
- Optional Spotify uses PKCE with a loopback callback and no client secret. Lyrics and Spotify use external services. Document conversion and Windows OCR are local.
- Active voice capture, microphone access and WhatsApp notification integration are disabled.

## Known limitations

**There is no application-level encryption at rest for SQLite, settings or the OAuth cache.** Do not treat local files as protected from another process running under the same Windows user account. A validated encryption/migration/recovery design remains future work; silently changing existing private data during repository publication would not be a safe substitute.

Temporary conversion cleanup covers normal lifecycle events. A forced crash/power failure can leave scratch files. The current launcher is not an installer, and distributing a runtime bundle requires a separate dependency/license review.

Historical development documents keep older decisions and references to local-only assets for context. Owner-specific workstation paths were replaced with placeholders such as `%USERPROFILE%` and `<project root>` on 27 October 2026; `tools/inventory_skills.py` writes the same placeholders. Original reference photos and ZIP archives remain excluded.

There is no web login, public upload service, remote SQL access, session-cookie layer or server-side account system. Web-specific protections such as RLS, login rate limiting and cookie flags must be designed if such a service is added; they are not represented as implemented here.

## Dependency and secret checks

The publication review uses Gitleaks with redacted output for staged content and Git history, plus pip-audit for the active Python dependency closure. Tools run outside the Kai runtime and are not production dependencies. Weekly Dependabot configuration is included for `kai/requirements.txt`.

A clean advisory scan is limited to the scanner/database/time and packages covered. It does not audit every native Windows/Qt/PDFium component, detect every secret type, prove the absence of vulnerabilities or replace review of untrusted files. See [the dated publication review](docs/19-github-and-privacy.md).

## Reporting

Report security concerns privately to the repository owner using an existing private channel. If GitHub private vulnerability reporting is enabled for the repository, use it. Do not post real tokens, clipboard contents, private documents or database files in an issue. Use a synthetic reproduction and redact logs/screenshots.

The source is a personal prototype with no commercial security SLA. Only report an issue as fixed after reviewing the change and running the relevant checks.
