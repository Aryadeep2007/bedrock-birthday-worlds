# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial framework structure
- Photo processing (pixel art & map art)
- World generator with 7 zones
- Behavior pack with Script API
- Resource pack with custom sounds
- Build automation (PowerShell scripts)
- Validation suite
- CI/CD pipeline
- Documentation (README, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY)

### Changed
- N/A

### Fixed
- N/A

## [1.0.0] - 2026-10-31

### Added
- Complete birthday world framework for Minecraft Bedrock v1.26.60+
- 7-zone adventure world template
- 14 hidden gifts system
- 7-clue treasure hunt
- Personalized photo gallery (pixel art & map art)
- Voice message integration
- Fireworks celebrations
- Birthday cake interaction
- Grand finale arena
- Configuration-driven customization
- Privacy-first architecture
- Comprehensive documentation

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-10-31 | Initial release |

## Upgrade Guide

### From 0.x to 1.0.0

This is the initial release - no upgrade needed.

---

## Release Checklist

For maintainers releasing new versions:

- [ ] Update version in relevant files
- [ ] Update CHANGELOG.md with release notes
- [ ] Run `.\scripts\validate.ps1 -Strict`
- [ ] Run `.\scripts\package.ps1 -Version X.Y.Z -IncludeTemplates -IncludeDocs`
- [ ] Create GitHub Release with artifacts
- [ ] Tag release: `git tag vX.Y.Z && git push --tags`
- [ ] Announce in discussions/social media