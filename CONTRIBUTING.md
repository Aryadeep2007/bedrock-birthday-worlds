# Contributing to Bedrock Birthday Worlds

Thank you for your interest in contributing! This project helps people create magical birthday experiences in Minecraft Bedrock Edition. Your contributions make that possible for more people.

## 🎯 Ways to Contribute

- **Bug Reports** - Found an issue? Let us know!
- **Feature Requests** - Have an idea for a new zone, gift type, or feature?
- **Code Contributions** - Fix bugs, add features, improve performance
- **Documentation** - Improve guides, add examples, fix typos
- **Translations** - Help make this accessible in more languages
- **Testing** - Test builds on different devices/versions

## 🚀 Getting Started

### Prerequisites

- Python 3.8+ with pip
- Node.js 18+ with npm
- Git
- Minecraft Bedrock Edition (for testing)

### Development Setup

```bash
# Fork and clone
git clone https://github.com/yourusername/bedrock-birthday-worlds.git
cd bedrock-birthday-worlds

# Run setup
.\scripts\setup.ps1 -InstallPythonPackages -InstallNodePackages

# Create a feature branch
git checkout -b feature/your-feature-name
```

## 📋 Development Guidelines

### Code Style

**Python** (photo processing, generators, packaging):
- Follow PEP 8
- Type hints for all functions
- Docstrings for public functions
- Max line length: 100 chars

```python
def process_image(input_path: Path, output_path: Path, size: int = 128) -> Dict[str, Any]:
    """Process an image to pixel art.
    
    Args:
        input_path: Source image file
        output_path: Output directory
        size: Output dimension in blocks
        
    Returns:
        Processing result metadata
    """
    # Implementation
```

**JavaScript** (behavior pack scripts):
- ES2020+ syntax
- JSDoc comments for functions
- Use `const`/`let`, avoid `var`
- Async/await over promises

```javascript
/**
 * Handles player's first join - shows welcome sequence.
 * @param {Player} player - The player who joined
 */
function handleFirstJoin(player) {
    // Implementation
}
```

**PowerShell** (build scripts):
- Use approved verbs
- Comment-based help for all functions
- Strict mode: `Set-StrictMode -Version Latest`

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`

Examples:
```
feat(photo-processing): add support for animated GIF input
fix(packaging): correct UUID generation in manifest
docs(readme): update quick start steps for v1.2
test(generators): add unit tests for zone generation
```

### Pull Request Process

1. **Create PR** from your feature branch to `main`
2. **Fill template** - All sections required
3. **Pass CI** - All checks must pass
4. **Code Review** - Address reviewer feedback
5. **Squash Merge** - Maintains clean history

### PR Requirements

- [ ] All CI checks pass (`validate`, `test-build`)
- [ ] No private assets in changes (run `.\scripts\validate.ps1 -Strict`)
- [ ] Tests added/updated for new functionality
- [ ] Documentation updated if user-facing changes
- [ ] Commit messages follow convention
- [ ] No merge conflicts

## 🧪 Testing

### Run Validation Suite

```powershell
# Full validation (strict)
.\scripts\validate.ps1 -Strict

# Quick validation
.\scripts\validate.ps1
```

### Test Build

```powershell
# Test with example config
.\scripts\build.ps1 example -SkipPhotos -SkipAudio
```

### Manual Testing Checklist

- [ ] World imports without errors
- [ ] Spawn sequence works (fireworks, letter, audio)
- [ ] All 7 zones accessible
- [ ] Gift discovery tracking works
- [ ] Treasure hunt clues progress
- [ ] Birthday cake interaction
- [ ] Grand finale triggers
- [ ] Adventure mode enforced
- [ ] Resource pack textures load
- [ ] Behavior pack scripts run

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Build Pipeline                        │
├─────────────────────────────────────────────────────────┤
│  config/birthday-<name>.json  →  Private Configuration  │
│  private-assets/photos/       →  Personal Photos        │
│  private-assets/audio/        →  Voice Messages         │
└─────────────────────┬───────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│  build.ps1 orchestrates:                                 │
│  1. Photo Processing  →  Pixel Art / Map Art            │
│  2. Audio Conversion  →  .ogg format                    │
│  3. World Generation  →  Structures, paths, gifts       │
│  4. Pack Building     →  Resource + Behavior Packs      │
│  5. .mcworld Packaging →  Final importable file         │
└─────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Location | Responsibility |
|-----------|----------|----------------|
| Photo → Pixel Art | `src/photo-processing/photo_to_pixel_art.py` | Block-based art |
| Photo → Map Art | `src/photo-processing/photo_to_maps.py` | Map/item frame art |
| World Generator | `src/generators/world_generator.py` | Zone structures |
| Pack Builder | `src/packaging/build_mcworld.py` | .mcworld assembly |
| Behavior Scripts | `templates/behavior-pack/scripts/` | Gameplay logic |

## 🎨 Adding New Features

### New Zone Type

1. Add zone definition to `world_generator.py` `ZONES` dict
2. Add zone blocks/theme in `behavior-pack/scripts/main.js` `CONFIG.zones`
3. Add path connections in `PATHS` array
4. Update documentation

### New Gift Type

1. Add to `GIFT_LOCATIONS` in both generator and behavior pack
2. Add item to `giftTypes` in config schema
3. Update gift discovery logic if special behavior needed

### New Sound Effect

1. Add entry to `templates/resource-pack/sounds.json`
2. Add `.ogg` file to `templates/resource-pack/sounds/`
3. Reference in behavior pack with `playSound(player, "sound_id")`

## 📝 Documentation Standards

- **README.md** - User-facing, beginner-friendly
- **docs/** - Technical documentation, API references
- **Code comments** - Explain *why*, not *what*
- **CHANGELOG.md** - Keep updated with each release

## 🔒 Security & Privacy

**NEVER** commit:
- Personal photos (`private-assets/photos/`)
- Voice recordings (`private-assets/audio/`)
- Personal configs (`config/birthday-*.json`)
- Built `.mcworld` files (`private-builds/`)

Run `.\scripts\validate.ps1 -Strict` before committing to verify.

See [SECURITY.md](SECURITY.md) for full policy.

## 🏷️ Release Process

Maintainers only:

1. Update version in relevant files
2. Update `CHANGELOG.md`
3. Run `.\scripts\package.ps1 -Version X.Y.Z -IncludeTemplates -IncludeDocs`
4. Create GitHub Release with artifacts
5. Tag release: `git tag vX.Y.Z && git push --tags`

## 💬 Communication

- **Issues** - Bug reports, feature requests
- **Discussions** - Questions, ideas, showcase
- **PR Comments** - Code review feedback
- **Discord** - (If available) Real-time chat

## 📜 License

By contributing, you agree your contributions will be licensed under the MIT License.

---

**Questions?** Open a discussion or ask in a PR. We're happy to help!

**Thank you for making birthdays magical!** 🎂✨