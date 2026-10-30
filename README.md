# 🎂 Bedrock Birthday Worlds

> **Create personalized Minecraft Bedrock Edition birthday adventure worlds for your loved ones.**

[![Minecraft Bedrock](https://img.shields.io/badge/Minecraft-Bedrock%20v1.26.60+-green.svg)](https://www.minecraft.net/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://github.com/yourusername/bedrock-birthday-worlds/workflows/CI/badge.svg)](https://github.com/yourusername/bedrock-birthday-worlds/actions)

A professional, reusable framework for generating personalized `.mcworld` files for Minecraft Bedrock Edition. Create magical birthday adventures with custom photos, voice messages, hidden gifts, treasure hunts, and more!

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎁 **14 Hidden Gifts** | Discoverable birthday presents scattered across zones |
| 🗺️ **Treasure Hunt** | 7-clue mystery adventure with riddles |
| 🖼️ **Photo Gallery** | Personal photos converted to Minecraft pixel art |
| 🎵 **Voice Messages** | Play custom `.ogg` birthday greetings in-game |
| 🎆 **Fireworks Shows** | Spectacular displays at spawn and finale |
| 🏰 **7 Unique Zones** | Palace, Hall, Museum, Amusement Park, Forest, Vault, Arena |
| 📖 **Personalized Letter** | Custom birthday book in player inventory |
| 🎮 **Adventure Mode** | Protected structures, guided gameplay |
| 🔧 **Fully Configurable** | JSON-driven customization - no coding required |

---

## 🚀 Quick Start (10 Steps)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/bedrock-birthday-worlds.git
cd bedrock-birthday-worlds

# 2. Run setup (installs dependencies)
.\scripts\setup.ps1 -InstallPythonPackages -InstallNodePackages

# 3. Prepare your personal assets (PRIVATE - never committed)
mkdir -p private-assets/photos private-assets/audio
# Copy photos (JPG/PNG) to private-assets/photos/
# Copy voice message (.ogg) to private-assets/audio/birthday_message.ogg

# 4. Create your configuration
cp config/birthday.json config/birthday-maria.json
# Edit config/birthday-maria.json with your details

# 5. Build the world!
.\scripts\build.ps1 maria

# 6. Find your .mcworld file
# Output: private-builds/Happy_Birthday_Maria.mcworld

# 7. Double-click to import into Minecraft Bedrock

# 8. Play and enjoy! 🎉
```

---

## 📁 Repository Structure

```
bedrock-birthday-worlds/
├── config/                    # Configuration files
│   ├── birthday.json          # Schema & default config (public)
│   ├── birthday.schema.json   # JSON Schema for validation
│   └── birthday-*.json        # Personal configs (PRIVATE - gitignored)
├── templates/                 # Reusable pack templates
│   ├── resource-pack/         # Textures, sounds, models
│   └── behavior-pack/         # Scripts, gameplay logic
├── src/                       # Source code & generators
│   ├── photo-processing/      # Photo → pixel art / map art
│   ├── generators/            # World structure generation
│   └── packaging/             # .mcworld builder
├── assets/generic/            # Generic placeholder assets
├── examples/                  # Example configurations
├── scripts/                   # Build automation (PowerShell)
│   ├── setup.ps1              # Environment setup
│   ├── build.ps1              # Main build script
│   ├── validate.ps1           # Validation suite
│   └── package.ps1            # Release packaging
├── docs/                      # Documentation
├── .github/workflows/         # CI/CD pipelines
└── private-assets/            # YOUR ASSETS (gitignored!)
    ├── photos/                # Personal photos
    └── audio/                 # Voice messages
```

---

## 🎯 Configuration

Copy `config/birthday.json` to `config/birthday-<name>.json` and customize:

```json
{
  "birthdayPerson": {
    "name": "Maria",
    "age": 10,
    "birthDate": "2014-05-15"
  },
  "world": {
    "title": "Happy Birthday Maria",
    "description": "A magical 10th birthday adventure!",
    "spawnCoordinates": { "x": 0, "y": 64, "z": 0 }
  },
  "personalAssets": {
    "photosDirectory": "private-assets/photos/",
    "voiceMessagePath": "private-assets/audio/birthday_message.ogg",
    "personalLetter": "Happy Birthday Maria! ..."
  },
  "gallery": { "maxPhotos": 20, "pixelArtScale": 1 },
  "gifts": { "count": 14, "giftTypes": ["diamond", "emerald", "golden_apple"] },
  "treasureHunt": { "enabled": true, "clueCount": 7 },
  "audio": { "enabled": true, "volume": 1.0 },
  "fireworks": { "enabled": true, "showAtSpawn": true, "showAtFinale": true }
}
```

---

## 🛠️ Scripts Reference

| Script | Purpose |
|--------|---------|
| `setup.ps1` | Install dependencies, create directories, validate tools |
| `build.ps1 <name>` | Build personalized `.mcworld` from config |
| `validate.ps1` | Validate manifests, scripts, configs, `.mcworld` |
| `package.ps1` | Create release packages (source, templates, docs) |

### Build Options

```powershell
# Basic build
.\scripts\build.ps1 maria

# Custom output name
.\scripts\build.ps1 maria -OutputName "Maria_10th_Birthday.mcworld"

# Skip steps for faster iteration
.\scripts\build.ps1 maria -SkipPhotos -SkipAudio

# Clean build directory only
.\scripts\build.ps1 maria -CleanOnly
```

### Validation

```powershell
# Validate everything
.\scripts\validate.ps1

# Validate specific config build
.\scripts\validate.ps1 -ConfigName maria

# Validate specific .mcworld file
.\scripts\validate.ps1 -McworldPath "private-builds\Happy_Birthday_Maria.mcworld"

# Strict mode (warnings = errors)
.\scripts\validate.ps1 -Strict
```

---

## 📸 Photo Processing

Two conversion modes available:

### Pixel Art (Blocks) - Recommended for Large Displays
```bash
python src/photo-processing/photo_to_pixel_art.py \
  -i private-assets/photos \
  -o build/pixel_art \
  -W 128 -H 128 \
  -p extended \
  --orientation vertical
```
- Uses concrete, wool, terracotta blocks
- 64-color extended palette
- Generates `.mcfunction` files for in-game placement

### Map Art (Maps) - Recommended for Item Frames
```bash
python src/photo-processing/photo_to_maps.py \
  -i private-assets/photos \
  -o build/maps \
  -s 128 \
  --generate-placement
```
- Creates 128×128 map data
- Compatible with item frames
- Includes Floyd-Steinberg dithering

---

## 🔊 Audio Requirements

- **Format**: `.ogg` (Vorbis codec)
- **Sample Rate**: 44.1 kHz recommended
- **Duration**: 2-30 seconds
- **Conversion**: Use `moviepy` (included in setup) or `ffmpeg`:
  ```bash
  ffmpeg -i input.mp3 -c:a libvorbis output.ogg
  ```

---

## 🌍 World Zones

| Zone | Coordinates | Theme | Highlights |
|------|-------------|-------|------------|
| **Grand Birthday Kingdom** | (0, 64, 0) | Palace | Spawn, cake, fireworks |
| **Royal Celebration Hall** | (100, 64, 0) | Banquet | Feast tables, gifts |
| **Memory Museum** | (-100, 64, 0) | Museum | Photo gallery, clues |
| **Amusement & Adventure City** | (0, 64, 100) | Park | Rides, games, gifts |
| **Mystery Forest** | (0, 64, -100) | Forest | Treasure hunt, secrets |
| **Secret Birthday Vault** | (200, 64, 200) | Vault | 14th gift, locked |
| **Grand Finale Arena** | (-200, 64, -200) | Arena | Celebration, rewards |

---

## 🔒 Privacy & Security

**CRITICAL**: The following are **NEVER** committed to the public repository:

| Asset Type | Location | Gitignored |
|------------|----------|------------|
| Personal photos | `private-assets/photos/` | ✅ |
| Voice recordings | `private-assets/audio/` | ✅ |
| Personal configs | `config/birthday-*.json` | ✅ |
| Built worlds | `private-builds/*.mcworld` | ✅ |
| Personal letters | In config JSON | ✅ |

The `.gitignore` enforces this. **Always verify** before pushing:
```bash
git status  # Check no private files are staged
```

See [SECURITY.md](SECURITY.md) for full privacy policy.

---

## 🤝 Contributing

We welcome contributions! Please read:

- [Contributing Guide](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes with tests
4. Run validation: `.\scripts\validate.ps1 -Strict`
5. Submit a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Minecraft Bedrock Script API documentation
- Pillow, NumPy, MoviePy for image/audio processing
- The Minecraft add-on community

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/bedrock-birthday-worlds/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/bedrock-birthday-worlds/discussions)
- **Security**: See [SECURITY.md](SECURITY.md)

---

**Made with ❤️ for unforgettable birthdays**

*Give the gift of adventure!*