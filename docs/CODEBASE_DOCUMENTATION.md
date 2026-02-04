# Textype Codebase Documentation

## Overview

Textype is a terminal-based typing tutor application built with Textual (TUI framework) that helps users learn touch typing through structured lessons and real-time feedback. The application supports multiple keyboard layouts, progressive lessons, visual feedback for finger placement, and multiple practice modes including code and sentence practice.

## Enhanced Architecture Flow

### 1. Application Entry Point
- **File**: `main.py`
- **Class**: `TypingTutor` (extends `textual.app.App`)
- **Flow**: Application starts → Profile selection → Practice mode selection → Content generation → Typing practice → Performance evaluation

### 2. Core Components

#### Configuration System (`config.py` + `models.py`)
- **Purpose**: Hierarchical configuration management with profile support
- **Key Components**:
  - `config.py`: Hardcoded default values
  - `models.py`: `DEFAULT_CONFIG`, `INITIAL_PROFILE_OVERRIDES`, `UserProfile.get_config()`
  - Profile-specific overrides with fallback to defaults
- **Flow**: Profile config → Initial overrides → Default config → Hardcoded defaults

#### Data Models (`models.py`)
- **Purpose**: User progress tracking and configuration persistence
- **Key Class**: `UserProfile`
  - Tracks: current lesson, WPM record, total drills, configuration overrides
  - Enhanced: `get_config()` method, `config` property for merged configuration
  - Persistence: JSON files in user data directory (`~/.local/share/textype/`)
- **Flow**: Profile loaded on startup → Configuration merged → Updated during practice → Saved on exit

#### Curriculum Management (`curriculum.py`)
- **Purpose**: Lesson definitions and progression logic
- **Key Components**:
  - `LessonDict`: Typed dictionary for lesson configuration
  - `LESSONS`: List of 38+ lessons across multiple categories
  - Categories: Home row, foundation keys, numbers, symbols, sentence practice
  - Each lesson: name, algorithm, row, target accuracy/WPM, shift mode
- **Flow**: Lesson selection based on profile index → Algorithm dispatch → Text generation

#### Keyboard Layout (`keyboard.py`)
- **Purpose**: Physical keyboard representation and finger mapping
- **Key Components**:
  - `PhysicalKey` enum: Evdev scancodes for all keys
  - `KEYBOARD_ROWS`: Visual layout for UI display
  - `FINGER_MAP`: Touch typing finger assignments
  - `LAYOUT`: Practice rows (home, focus groups, numbers, symbols)
  - `DISPLAY_MAP`: Special key labels for display
- **Flow**: Used for visualization, practice text generation, and finger highlighting

#### Text Generation Algorithms (`algorithms_generator.py`)
- **Purpose**: Generate practice patterns for different lesson types
- **Algorithms**:
  1. `single_key_repeat`: Isolation practice (repeat each key)
  2. `same_hand_adjacent`: Finger neighbor practice (adjacent keys)
  3. `alternating_pairs`: Hand alternation practice (left-right pairs)
  4. `mirror_pairs`: Mirror finger practice (mirrored positions)
  5. `rolls`: Finger flow practice (inward/outward rolls)
  6. `pseudo_words`: Synthesis practice (random "words")
- **Flow**: Selected based on lesson → Generates physical key sequences → Converted to characters

#### Sentence Generation (`sentence_generator.py`)
- **Purpose**: Generate practice sentences from multiple sources
- **Sources**:
  1. `"local"`: Default sentences list from curriculum
  2. `"file"`: Read from external text file
  3. `"api"`: Fetch from external quote API
  4. `"cmd"`: Execute shell command for dynamic content
- **Flow**: Source selection → Content generation → Text normalization → Return sentence

#### Code Generation (`code_generator.py`)
- **Purpose**: Generate code snippets for programming language practice
- **Languages**: Python, Rust, C, C++
- **Sources**:
  1. `"local"`: Read from local snippets file
  2. `"file"`: Read from external code file
  3. `"cmd"`: Execute shell command (e.g., `grep -r 'def ' .`)
  4. `"ai"`: Generate using AI (Ollama/OpenAI)
- **Flow**: Language selection → Source processing → Code snippet generation → Normalization

#### Text Normalization (`text_normalizer.py`)
- **Purpose**: Normalize text for consistent typing practice
- **Functions**:
  - `normalize_text()`: Standardize whitespace, line endings, indentation
  - Handles: Tabs → spaces, multiple spaces → single, trailing whitespace removal
- **Flow**: Raw text input → Normalization → Clean practice text output

#### Layout Resolution (`xkb_resolver.py`)
- **Purpose**: Map physical keys to characters based on system keyboard layout
- **Key Class**: `XKBResolver`
  - Uses XKB library for layout-aware character resolution
  - Handles modifier keys (shift, altgr)
  - Caches results for performance
- **Flow**: Physical key + modifiers → XKB resolution → Character display/validation

#### UI Widgets (`widgets.py`)
- **Purpose**: Custom UI components and modal screens
- **Key Components**:
  - `FingerColumn`: Visual finger representation with height/width
  - `StatsScreen`: Drill results display with WPM/accuracy
  - `ProfileSelectScreen`: Profile management (create/select)
  - `ProfileInfoScreen`: Profile information display
- **Flow**: Integrated into main app for specialized UI needs

### 3. Enhanced Data Flow

```
User Input → on_key() → Character Validation → Progress Update
      ↓
Profile Load → Practice Mode Selection → Content Generation → Display
      ↓           ↓           ↓           ↓
    Curriculum   Sentences    Code     Pre-fetching
      ↓           ↓           ↓           ↓
Session Timer → Statistics Calculation → Performance Evaluation
      ↓
Profile Update → Progress Save → Next Content/Repeat
```

### 4. Key Processes

#### Session Management (`main.py:TypingTutor`)
1. **Session Start** (`start_new_session()`)
   - Reset all session statistics
   - Determine practice mode from profile
   - Generate practice text (synchronously or from pre-fetch)
   - Start 5-minute timer

2. **Practice Text Generation** (`_get_practice_text()`)
   - Check for pre-fetched content
   - Generate based on practice mode:
     - `"curriculum"`: Use `generate_lesson_text()`
     - `"sentences"`: Use `generate_sentence()`
     - `"code"`: Use `generate_code_snippet()`
   - Start background pre-fetching for next chunk

3. **Typing Validation** (`on_key()`)
   - Map character to physical key using `char_to_physical`
   - Compare with expected physical key from `target_keys`
   - Update accuracy and error counts
   - Handle hard/soft mode differences
   - Check for chunk completion

4. **Display Update** (`refresh_display()`)
   - Calculate real-time WPM and accuracy
   - Update statistics bar with mode/language info
   - Highlight current key and finger
   - Show shift key requirement

5. **Progress Evaluation** (`evaluate_drill_and_show_stats()`)
   - Calculate final statistics
   - Check against lesson requirements (curriculum mode only)
   - Update profile progress and records
   - Show results screen based on preference

#### Content Generation Flow
```
Practice Mode → Source Selection → Content Generation
     ↓              ↓                  ↓
Curriculum      Algorithm        Physical Keys
Sentences       Source (api/file/cmd)  Sentence
Code            Language + Source      Code Snippet
     ↓                  ↓                  ↓
Shift Mode      Text Normalization    XKB Resolution
     ↓                  ↓                  ↓
Rendered Text   Clean Practice Text   Character Display
```

### 5. Enhanced Configuration System

#### Profile Overrides Hierarchy
1. **Profile `config_overrides`** (Highest priority)
   - User-specific customizations
   - Includes `INITIAL_PROFILE_OVERRIDES` for new profiles
   - Saved in profile JSON file
   - Includes: `PRACTICE_MODE`, `CODE_LANGUAGES`, UI preferences

2. **`DEFAULT_CONFIG`** (models.py)
   - Application-wide sensible defaults
   - Source configurations, API endpoints, file paths
   - Fallback when not in profile overrides

3. **Hardcoded `config.py` values** (Lowest priority)
   - Fallback when no profile exists
   - Used before profile selection

**Note**: `INITIAL_PROFILE_OVERRIDES` provide better UX defaults (show keyboard/fingers by default)
and are copied into `config_overrides` when a new profile is created.

#### Practice Modes
1. **`"curriculum"`**: Structured lesson progression (38+ lessons)
2. **`"sentences"`**: Sentence practice from multiple sources
3. **`"code"`**: Programming language code snippets

### 6. Error Handling and Validation

#### Validation Logic
1. **Primary**: Physical key match (strict touch typing)
2. **Fallback**: Character match (for unmapped keys or edge cases)
3. **Hard Mode**: Errors prevent character addition to typed text
4. **Soft Mode**: Errors allow continuation (for learning)

#### Layout Compatibility
- `XKBResolver` uses system keyboard layout via environment
- `char_to_physical` mapping built at startup with shift states
- Supports learning different layouts without OS changes
- Automatic fallback to character matching for compatibility

#### Content Source Fallbacks
- API failures → fallback to file → fallback to local defaults
- Command execution timeouts → fallback to next source
- File not found → fallback to built-in content
- AI generation failures → fallback to local snippets

### 7. Performance Optimizations

#### Asynchronous Pre-fetching
- **Purpose**: Eliminate generation delays between chunks
- **Implementation**: `_start_prefetching()` background task
- **Flow**: Current chunk typing → Background generation → Store in cache → Immediate next chunk
- **Benefits**: Smooth user experience, no waiting for content generation

#### Caching Strategies
1. **Character Mapping**: `char_to_physical` built once at startup
2. **Key Labels**: `_key_label_cache` for keyboard display
3. **Shift States**: `_key_char_cache` for shift/unshift characters
4. **XKB Resolution**: Cached within `XKBResolver` class

#### Memory Management
- Profile data loaded on demand (not all profiles at once)
- Practice text generated per session/chunk
- Pre-fetched content limited to next chunk only
- No persistent in-memory cache of all content

### 8. UI/UX Design

#### Visual Feedback
- **Color Coding**: Green correct, red incorrect, reverse current
- **Active Highlighting**: Current key and corresponding finger
- **Shift Indication**: Automatic shift key highlighting
- **Mode Indicators**: Practice mode and language in stats bar
- **Progress Visualization**: Finger columns show relative usage

#### Navigation and Controls
- **F1**: Toggle keyboard visualization
- **F2**: Toggle finger guide
- **F3**: Toggle auto-stats preference
- **F4**: Switch/create profile
- **Enter**: Start new session
- **Escape**: Save and quit
- **Ctrl+R**: Repeat current lesson

#### Screen Management
- **Main Screen**: Typing practice with stats and visualizations
- **Profile Selection**: List existing + create new profiles
- **Stats Screen**: Drill results with pass/fail status
- **Profile Info**: Current profile details and configuration

### 9. File Structure

```
textype/
├── __init__.py          # Package initialization
├── __about__.py         # Version information
├── main.py              # Main application (TypingTutor class)
├── config.py            # Hardcoded configuration constants
├── models.py            # Data models (UserProfile, configuration system)
├── curriculum.py        # Lesson definitions and progression
├── keyboard.py          # Keyboard layout and physical key definitions
├── algorithms_generator.py  # Practice pattern generation algorithms
├── sentence_generator.py    # Sentence generation from multiple sources
├── code_generator.py        # Code snippet generation for programming languages
├── text_normalizer.py       # Text normalization utilities
├── xkb_resolver.py      # Layout-aware key resolution (XKB-based)
├── widgets.py           # Custom UI components and screens
├── styles.tcss          # Textual stylesheet
```

### 10. Dependencies

#### Core Dependencies
- **textual**: TUI framework for terminal applications
- **xkbcommon**: Keyboard layout handling (via python-xkbcommon)
- **platformdirs**: Cross-platform user data directories
- **rich**: Text formatting and styling

#### Optional Dependencies
- **requests**: HTTP client for API-based content sources
- **aiohttp**: Asynchronous HTTP for AI generation (if needed)

#### System Dependencies
- **XKB library**: System keyboard layout support
- **Evdev headers**: For physical key scancodes (development)

### 11. Extension Points

#### Adding New Practice Modes
1. Add mode identifier to `PRACTICE_MODE` configuration
2. Implement generation function in appropriate module
3. Add handling in `_get_practice_text()` method
4. Update profile configuration UI if needed

#### Supporting New Content Sources
1. Add source identifier to `SENTENCE_SOURCE`/`CODE_SOURCE`
2. Implement generation logic in generator module
3. Add fallback chain in generation function
4. Update configuration defaults if needed

#### Adding New Algorithms
1. Add function to `algorithms_generator.py`
2. Update `_generate_physical_keys()` dispatch dictionary
3. Add lesson definitions in `curriculum.py`
4. Test with different keyboard rows

#### Customizing Keyboard Layouts
1. Modify `LAYOUT` dictionary in `keyboard.py`
2. Add corresponding lesson definitions
3. Update finger mappings if needed
4. Test with visual keyboard display

### 12. Testing Strategy

#### Manual Testing Areas
1. **Practice Modes**: Curriculum, sentences, code modes
2. **Content Sources**: Local, file, API, command, AI sources
3. **Layout Compatibility**: Different system keyboard layouts
4. **Error Handling**: Hard/soft mode, validation edge cases
5. **UI Responsiveness**: All screen sizes and terminal emulators
6. **Profile Persistence**: Save/load cycles, configuration merging

#### Automated Testing Potential
- Unit tests for generator algorithms
- Integration tests for session flow
- UI component testing with Textual
- Configuration resolution tests
- Content source fallback tests

#### Performance Testing
- Memory usage with long sessions
- Pre-fetching latency measurements
- XKB resolution performance
- UI refresh rates under load

### 13. Deployment and Distribution

#### Installation
```bash
# From source
git clone <repository>
cd textype
pip install -e .
```

#### Configuration Files
- **User profiles**: `~/.local/share/textype/*.json`
- **Sentence file**: `sentences.txt` (customizable path)
- **Code snippets**: `snippets.py` (customizable path)
- **API configuration**: Environment variables for API keys

#### Platform Support
- **Linux**: Full support (XKB, evdev)
- **macOS**: Basic support (keyboard layout may differ)
- **Windows**: Limited support (XKB not available)

This documentation provides a comprehensive overview of the enhanced Textype codebase structure, data flow, and extension points for maintenance and development.
