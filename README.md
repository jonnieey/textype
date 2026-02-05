# Textype - Terminal Typing Tutor

A modern, feature-rich typing tutor for the terminal with multiple practice modes, real-time feedback, and progress tracking.

## GIF Preview

![](https://github.com/jonnieey/textype/blob/main/docs/textype.gif)

## Features

### 🎯 Multiple Practice Modes
- **Curriculum Mode**: 38+ structured lessons (home row, foundation keys, numbers, symbols)
- **Sentences Mode**: Practice with quotes and sentences from multiple sources
- **Code Mode**: Type real code snippets in Python, Rust, C, and C++

### 🚀 Smart Content Generation
- **Local files**: Use built-in or custom practice content
- **External APIs**: Fetch quotes from online sources
- **Shell commands**: Generate dynamic content from your system
- **AI integration**: Generate practice content with AI (Ollama/OpenAI)

### ⚡ Performance Optimizations
- **Async pre-fetching**: Next chunk loads in background
- **Real-time stats**: WPM, accuracy, errors with live updates
- **Visual feedback**: Keyboard highlighting, finger guides, color coding

### 🔧 Customization
- **Profile-based**: Save progress and preferences per user
- **Configuration hierarchy**: Global defaults → profile overrides
- **Practice settings**: Adjust difficulty, content sources, UI visibility

## Quick Start

### Installation
```bash
# From source
git clone https://github.com/jonnieey/textype
cd textype
uv tool install . or pip install -e .

```

### Basic Usage
```bash
# Start the application
textype

# Or run directly
python -m textype.main
```

### Navigation
- **F1**: Toggle keyboard visualization
- **F2**: Toggle finger guide
- **F3**: Toggle auto-stats display
- **F4**: Switch/create profile
- **F5**: Show Profile Info
- **F6**: Switch practice mode
- **CTRL+Q**: Exit

## Practice Modes

### 1. Curriculum Mode
Structured progression through 38+ lessons:
- **Home row**: Isolation, adjacency, alternating, mirroring, rolls, synthesis
- **Foundation keys**: Focus on specific key pairs (E/I, R/U, T/O, etc.)
- **Numbers & symbols**: Special character practice
- **Sentence practice**: Build up to full sentence typing

### 2. Sentences Mode
Practice with meaningful text:
- **Local**: Built-in practice sentences
- **File**: Custom sentences from text file
- **API**: Quotes from online sources
- **Command**: Dynamic content from shell commands

### 3. Code Mode
Type real programming code:
- **Languages**: Python, Rust, C, C++
- **Sources**: Local snippets, external files, AI generation
- **Benefits**: Learn coding syntax while improving typing

## Configuration

### Profile Settings
User profiles store:
- Current lesson progress
- Personal best WPM records
- Configuration overrides
- Practice mode preferences

### Configuration Hierarchy
1. **Profile overrides** (user customizations)
2. **Default config** (application defaults)
3. **Hardcoded values** (fallback)

### Key Settings
```python
# Practice mode
PRACTICE_MODE = "curriculum"  # "curriculum", "sentences", "code"

# Content sources
SENTENCE_SOURCE = "api"       # "local", "file", "api", "cmd"
CODE_SOURCE = "local"         # "local", "file", "cmd", "ai"

# UI preferences
SHOW_QWERTY = True           # Show keyboard visualization
SHOW_FINGERS = True          # Show finger guide
HARD_MODE = True            # Errors prevent progress
```

## Architecture

### Core Modules
- **`main.py`**: Application entry point and session management
- **`config.py`**: Configuration constants
- **`models.py`**: User profiles and data persistence
- **`curriculum.py`**: Lesson definitions and progression
- **`keyboard.py`**: Physical keyboard layout and mappings
- **`algorithms_generator.py`**: Practice pattern algorithms
- **`sentence_generator.py`**: Sentence content generation
- **`code_generator.py`**: Code snippet generation
- **`xkb_resolver.py`**: Keyboard layout resolution
- **`widgets.py`**: Custom UI components

### Data Flow
```
User Input → Validation → Progress Update
      ↓
Profile → Mode Selection → Content Generation
      ↓
Session Timer → Statistics → Evaluation → Save
```

## Development

### Project Structure
```
textype/
├── main.py              # Main application
├── config.py            # Configuration
├── models.py            # Data models
├── curriculum.py        # Lesson definitions
├── keyboard.py          # Keyboard layout
├── algorithms_generator.py  # Practice algorithms
├── sentence_generator.py    # Sentence generation
├── code_generator.py        # Code generation
├── xkb_resolver.py      # Layout resolution
├── widgets.py           # UI components
├── styles.tcss          # Textual stylesheet
└── docs/                # Documentation
```

### Dependencies
- **textual**: TUI framework
- **xkbcommon**: Keyboard layout handling
- **platformdirs**: Cross-platform user directories
- **rich**: Text formatting

### Extending
- **New algorithms**: Add to `algorithms_generator.py`
- **New content sources**: Extend generator modules
- **New practice modes**: Add mode handling in `main.py`
- **Custom layouts**: Modify `keyboard.py` LAYOUT dictionary

## Documentation

Comprehensive documentation available in `docs/`:
- `CODE_FLOW_DOCUMENTATION.md`: Detailed function and data flow
- `CODEBASE_DOCUMENTATION.md`: Architecture overview
- `*.dot` files: Graphviz flow diagrams

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## Support

- **Issues**: Report bugs or request features
- **Documentation**: See `docs/` directory for detailed information
- **Development**: Check architecture documentation for extending functionality

---

**Textype** - Type smarter, code faster, learn better.
