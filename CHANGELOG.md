# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.1] - 2026-09-04

### Fixed
- The dataset version table listed six releases and gave no way to tell four of them apart. JudgeGPT 1.1.0 and 1.2.0 both showed 539 participants, 2,546 judgments and the same 11 March 2026 snapshot; RogueGPT 1.1.0 and 1.2.0 both showed 3,278 fragments and the same 23 March 2026 snapshot. A `What changed` column now states, from the deposit descriptions, that both current versions are corrections rather than additions: JudgeGPT 1.2.0 replaced the participant table with a privacy-reduced publication copy and made its bundled corpus byte-identical to RogueGPT 1.2.0, and RogueGPT 1.2.0 corrected the export so the style, format and seed-phrase fields are populated for the 2,257 fragments that carry them.

### Changed
- The dataset access paragraph stated that the data are shared under terms requiring ethical review, which is true and incomplete. The stimulus corpus has no single licence: the 2,638 machine-generated fragments and all accompanying documentation are released under CC BY 4.0, while 640 fragments are excerpts of third-party news material that the depositor cannot license. Every record states its provenance, so the machine-generated subset can be separated.
- `CITATION.cff` declares version 1.3.1.

## [1.3.0] - 2026-09-01

### Fixed
- The data exporter derived its CSV column set from the first documents it saw, via `pd.DataFrame`. The collections are schema-flexible, so column membership depended on the order MongoDB returned documents in, and fields carried only by later records were dropped without warning. This is what caused the published corpus to ship 12 of its 15 columns. The column set is now the union of all keys across all documents, sorted for stable ordering. `pandas` is no longer required for the export.

### Changed
- Location and query parameters are reduced before they reach the database. The geolocation response becomes `IpCountry` and `IpContinent`, the query parameters become a `RecruitmentRoute` label, and the raw values are never stored. The user agent and screen resolution are no longer collected at all. Previously the full geolocation response, user agent, screen resolution and verbatim query parameters were stored; none were used by any analysis, and together they identified individuals.
- The privacy policy names freeipapi.com and its operator, states that the lookup is performed by the participant's browser and that their IP address is therefore disclosed to that service, and lists what is discarded before storage. Present in all four languages.
- The consent text describes the same, and no longer claims that browser and screen information are collected.
- Dataset references updated to the current releases: perception data 10.5281/zenodo.22226580 (v1.2.0), stimulus corpus 10.5281/zenodo.22225536 (v1.2.0).
- `CITATION.cff` now declares `version` and `date-released`, which it previously omitted entirely.

### Documentation
- `DATA_DICTIONARY.md` documents `IpCountry`, `IpContinent` and `RecruitmentRoute`, and adds a section on what is deliberately not collected and why. Records collected before this release may still carry the four original fields; they are withheld from the published deposit in every case.
- The fragment validation rules note that the released corpus was checked against them.

### Translated
- `docs/es/consent.md` and `docs/fr/consent.md` contained the English text and are now translated.

## [1.2.1] - 2026-08-16

### Documentation
- Stimulus description now cites the released corpus snapshot (10 models across
  6 providers) rather than RogueGPT's model registry, which is deliberately
  broader than any single snapshot.
- Headline participant and judgment counts updated to the current 539 / 2,546
  snapshot.
- Project page restored after an empty-file commit, with the ACM DOI on the
  "Eroding the Truth-Default" card corrected and the Zenodo badge pointed at the
  concept DOI.
- Dataset version table added; WWW '26 Companion citation month and page numbers
  corrected.

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
