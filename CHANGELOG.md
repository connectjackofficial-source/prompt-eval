# Changelog

## 0.7.0 - 2026-10-14

- `compare_prompts()` — head-to-head A/B of two prompt strategies on the
  same cases (score first, latency breaks ties)

## 0.6.0 - 2026-10-14

- `rank_cases()` — run every case and rank results: failures first, then
  by latency, so the weakest prompt behaviors surface first

## 0.5.0 - 2026-10-10

- `cases_from_dict()` — build cases from plain dict/JSON specs
- `CHECKER_BUILDERS` registry for named checkers

## 0.4.0 - 2026-10-10

- `Report.to_json()` machine-readable reports
- `run_and_save()` writes the report to a file

## 0.3.0 - 2026-10-08

- `starts_with` / `ends_with` checkers
- Per-case latency tracking (`timings`, `avg_latency_ms`)

## 0.2.0 - 2026-10-06

- Score (pass rate) in reports

## 0.1.0 - 2026-09-29

- Initial release
- Case, contains, matches, not_contains, length_between checkers
- run() and Report
