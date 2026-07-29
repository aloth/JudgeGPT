# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-07-29

### Added
- Continuous integration (`.github/workflows/ci.yml`) running on Python 3.11 and 3.12:
  dependency install smoke test, `import app` smoke test, and the test suite.
- Test suite (`tests/test_challenge.py`, 11 cases) covering challenge-link
  encoding and decoding, including a frozen v1.1.0 token fixture that guards
  against silently breaking already-shared challenge URLs, and malformed-input
  handling for tokens arriving from URL parameters.
- `CHANGELOG.md`.

### Changed
- README restructured so the participation hook and live study numbers appear
  above the fold; the research mandate moved below.
- Dependencies are now version-bounded (`streamlit>=1.40,<2`, `pymongo>=4.6,<5`,
  `streamlit-javascript>=0.1.5,<0.2`) instead of unpinned.

### Fixed
- Removed `uuid` and `datetime` from `requirements.txt`. Both are Python
  standard-library modules, but PyPI packages of the same name exist as
  obsolete Python-2-era shims. Installing them could shadow or break the
  stdlib modules, so `pip install -r requirements.txt` could corrupt a fresh
  environment.

### Notes
- The dependency bounds are technically a compatibility change for anyone who
  previously ran an unpinned, older Streamlit. Released as a minor version
  since the application behavior and data schema are unchanged.

## [1.1.0] - 2026-02-23

### Added
- Post-response reveal, challenge mode, and social sharing score cards.

[1.2.0]: https://github.com/aloth/JudgeGPT/releases/tag/v1.2.0
[1.1.0]: https://github.com/aloth/JudgeGPT/releases/tag/v1.1.0
