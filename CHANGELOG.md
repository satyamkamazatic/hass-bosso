# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-05-06

### Added
- HTTP request timeouts (15s total, 5s connect) to prevent hangs on slow backends
- Defensive handling of missing fields in API responses
- Empty-data guards in light and select platforms

### Changed
- Production API URL (`https://be.bosso.biz`) is now the default
- Replaced bare `except Exception` with proper exception class handling for HA compatibility
- Network errors and auth errors are now distinguished with separate user messages

### Fixed
- Integration would hang indefinitely if backend was unresponsive

## [1.0.0] - 2026-05-06

### Added
- Initial public release
- Email/password authentication with automatic token refresh
- Light entity per Bosso device (on/off, brightness, RGB color, color temperature)
- Effect support (Solid, Rainbow, etc.) from the Bosso effects catalog
- Predefined preset selection via dedicated select entity
- User-defined preset selection via dedicated select entity
- Preset i-array resizing to match device LED count
- Multi-device support with pagination
