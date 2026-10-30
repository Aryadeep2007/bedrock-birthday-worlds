# Security & Privacy Policy

## 🔒 Privacy First Design

This project is built with **privacy by design**. Personal birthday assets (photos, voice messages, letters, configs) are **never** stored in or published to the public repository.

## 📋 What Stays Private (NEVER COMMITTED)

| Category | Examples | Location |
|----------|----------|----------|
| **Photos** | Birthday person's pictures, family photos | `private-assets/photos/` |
| **Audio** | Voice messages, birthday songs | `private-assets/audio/` |
| **Personal Config** | Name, age, birth date, custom letter | `config/birthday-*.json` |
| **Built Worlds** | Generated `.mcworld` files | `private-builds/` |
| **Personal Letters** | Custom birthday messages | In config JSON |

## ✅ What IS Public (Safe to Share)

| Category | Examples |
|----------|----------|
| **Framework Code** | All Python, JS, PowerShell scripts |
| **Templates** | Resource/behavior pack structures |
| **Documentation** | README, guides, API docs |
| **Generic Assets** | Placeholder textures, sounds |
| **Config Schema** | `config/birthday.json` (template only) |
| **Examples** | Sanitized example configurations |

## 🛡️ Enforcement Mechanisms

### 1. .gitignore Rules

```gitignore
# Private assets - NEVER COMMIT THESE
private-assets/
private-builds/
personal-config/
*.mcworld

# Personal configuration
config/birthday-*.json
!config/birthday.json
!config/birthday.schema.json
```

### 2. Pre-commit Validation

Run before every commit:
```powershell
.\scripts\validate.ps1 -Strict
```

This checks:
- No files in `private-assets/`, `private-builds/`, `personal-config/`
- No `*.mcworld` files tracked
- No `config/birthday-*.json` files tracked (except template)

### 3. CI/CD Checks

GitHub Actions workflow (`.github/workflows/ci.yml`) validates:
- No private directories have tracked files
- `.gitignore` contains required patterns
- Manifest files are valid

## 🚨 Reporting Security/Privacy Issues

If you discover a privacy leak or security vulnerability:

1. **DO NOT** create a public issue
2. **Email** the maintainers directly: security@bedrock-birthday-worlds.example.com
3. **Or** use GitHub's private vulnerability reporting

We will:
- Acknowledge within 48 hours
- Investigate and fix promptly
- Coordinate disclosure if needed

## 🔐 Data Handling

### Local Processing Only

All personal asset processing happens **locally on your machine**:
- Photos → pixel art conversion
- Audio → .ogg conversion
- World generation
- .mcworld packaging

**No data is uploaded** to any external service during the build process.

### Configuration Data

Your `config/birthday-<name>.json` contains:
- Name, age, birth date
- File paths to personal assets
- Custom birthday letter text

This file **never leaves your computer** unless you explicitly share it.

## 📦 Distribution Safety

When sharing your built `.mcworld` file:
- It contains your photos (as pixel art), voice message, and letter
- Only share with trusted recipients
- The `.mcworld` is a standard Minecraft package - anyone with it can import and play

## 🧹 Cleanup

After building and sharing:
```powershell
# Clean build artifacts (keeps private assets)
.\scripts\build.ps1 <name> -CleanOnly

# Or manually:
Remove-Item private-builds\.build_* -Recurse -Force
```

## 📋 Compliance

This project follows:
- **GDPR principles** - Data minimization, local processing, user control
- **COPPA awareness** - Designed for family use, no child data collection
- **Minecraft EULA** - Complies with Minecraft add-on guidelines

## 🔍 Verification Checklist

Before pushing to any public repository:

- [ ] Run `.\scripts\validate.ps1 -Strict` - passes with 0 errors
- [ ] Run `git status` - no private files shown
- [ ] Check `git diff --cached` - no private files staged
- [ ] Verify `.gitignore` covers all private patterns
- [ ] Confirm no hardcoded personal paths in committed code

## 📞 Contact

For privacy/security questions:
- **Email**: security@bedrock-birthday-worlds.example.com
- **GitHub**: Private vulnerability report

---

**Remember**: This framework empowers you to create personal gifts. The privacy of those gifts is your responsibility - the tools help, but you control the data.