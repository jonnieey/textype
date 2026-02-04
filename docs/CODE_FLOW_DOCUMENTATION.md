# Textype Code Flow Documentation

## Overview
This document traces the flow of configuration values, function calls, and data transformations through the Textype typing tutor application. We'll follow concrete examples from configuration through to user interaction.

## Key Changes in Current Architecture

### New Features Added:
1. **Multiple Practice Modes**: Curriculum, Sentences, and Code practice modes
2. **Dynamic Content Generation**: Support for local files, commands, APIs, and AI-generated content
3. **Asynchronous Pre-fetching**: Background generation of next practice chunk
4. **Enhanced Configuration System**: Profile-specific configuration with defaults and overrides
5. **Code Practice**: Support for Python, Rust, C, and C++ code snippets
6. **Sentence Generation**: Multiple sources including local files and external APIs

## 1. Configuration Flow: Enhanced Profile-Based Configuration

### Step 1: Default Configuration Definition
**File**: `config.py:8-47`
```python
SHOW_QWERTY: bool = False
SHOW_FINGERS: bool = False
HARD_MODE: bool = True
SHOW_STATS_ON_END: bool = False
DRILL_DURATION: int = 300
SHUFFLE_AFTER: int = 5

# Practice source configurations
SENTENCE_SOURCE: str = "api"
CODE_SOURCE: str = "local"
```

### Step 2: Profile Configuration System
**File**: `models.py:18-37`
```python
DEFAULT_CONFIG: Dict[str, Any] = {
    "SHOW_QWERTY": False,
    "SHOW_FINGERS": False,
    "HARD_MODE": True,
    "SHOW_STATS_ON_END": False,
    "DRILL_DURATION": 300,
    "SHUFFLE_AFTER": 5,
    "SENTENCE_SOURCE": "api",
    "CODE_SOURCE": "local",
    "PRACTICE_MODE": "curriculum",
    "CODE_LANGUAGES": "python,rust,c,cpp",
}

INITIAL_PROFILE_OVERRIDES: Dict[str, Any] = {
    "SHOW_QWERTY": True,  # Show keyboard by default for new users
    "SHOW_FINGERS": True,  # Show finger guide by default for new users
    "SHOW_STATS_ON_END": True,  # Show stats automatically for new users
}
```

### Step 3: Configuration Resolution
**File**: `main.py:115-121`
```python
def _get_config(self, key: str) -> Any:
    """Get configuration value from profile or fallback to default."""
    if self.profile:
        return self.profile.get_config(key)
    else:
        return getattr(config, key)
```

### Step 4: UI Composition with Dynamic Configuration
**File**: `main.py:136-137`
```python
kb_classes = "" if self._get_config("SHOW_QWERTY") else "hidden"
```

**Result**: Configuration is now profile-aware, with defaults, profile overrides, and runtime resolution.

## 2. Practice Text Generation Flow: Multi-Mode System

### Step 1: Practice Mode Selection
**File**: `main.py:717-724`
```python
if self.profile:
    practice_mode = self.profile.config_overrides.get(
        "PRACTICE_MODE", "curriculum"
    )
```

### Step 2: Mode-Specific Text Generation

#### Mode A: Curriculum Mode (Lesson-Based)
**File**: `main.py:1192-1208`
```python
def generate_lesson_text(self) -> str:
    lesson = LESSONS[self.profile.current_lesson_index]
    algo_type = lesson.get("algo")

    # Handle sentence algorithm specially
    if algo_type == "sentence":
        return self._generate_sentence_text()

    row_key = lesson.get("row", "home")
    row_data = LAYOUT.get(row_key)

    # Generate physical keys using appropriate algorithm
    physical_keys = self._generate_physical_keys(algo_type, row_data)
    self.target_keys = physical_keys

    # Convert physical keys to characters
    shift_mode = lesson.get("shift_mode", "off")
    return self._render_keys_to_text(physical_keys, shift_mode)
```

#### Mode B: Sentences Mode
**File**: `main.py:753-756`
```python
if practice_mode == "sentences":
    sentence = generate_sentence(self.profile.config)
    self.target_keys = self._sentence_to_physical_keys(sentence)
    return sentence
```

**File**: `sentence_generator.py:21-33`
```python
def generate_sentence(config_overrides: Optional[Dict[str, Any]] = None) -> str:
    """Generate a random practice sentence."""

    def get(key):
        if config_overrides and key in config_overrides:
            return config_overrides[key]
        return getattr(config, key)

    source = get("SENTENCE_SOURCE")
```

#### Mode C: Code Mode
**File**: `main.py:757-766`
```python
elif practice_mode == "code":
    # Get language list from config
    languages_str = self.profile.config_overrides.get(
        "CODE_LANGUAGES", "python,rust,c,cpp"
    )
    languages = [lang.strip() for lang in languages_str.split(",")]
    language = random.choice(languages)

    snippet = code_generator.generate_code_snippet(
        language, self.profile.config
    )
    self.target_keys = self._sentence_to_physical_keys(snippet)
    self.current_code_language = language
    return snippet
```

### Step 3: Asynchronous Pre-fetching
**File**: `main.py:716-744`
```python
# Check if we have pre-fetched content for the current mode
if self.profile:
    practice_mode = self.profile.config_overrides.get(
        "PRACTICE_MODE", "curriculum"
    )
    if (
        self._prefetched_text is not None
        and self._prefetched_mode == practice_mode
    ):
        # Use pre-fetched content
        text = self._prefetched_text
        keys = self._prefetched_keys
        language = self._prefetched_language

        # Clear pre-fetched data (we're consuming it)
        self._prefetched_text = None
        self._prefetched_keys = None
        self._prefetched_language = None
        self._prefetched_mode = None

        # Set target keys and language
        self.target_keys = keys
        if language:
            self.current_code_language = language

        # Start pre-fetching the next chunk in background
        self._start_prefetching()

        return text
```

## 3. Enhanced Lesson Generation Flow

### Step 1: Expanded Curriculum Structure
**File**: `curriculum.py:26-381`
```python
rows: Tuple[str, ...] = ("home",)
LESSONS: List[LessonDict] = []

# Home row lessons (7 sub-lessons) as per original
for idx, row in enumerate(rows, start=1):
    LESSONS.extend([
        LessonDict(name=f"{idx}.1: Isolation", algo="repeat", row=row, ...),
        LessonDict(name=f"{idx}.2: Adjacency", algo="adjacent", row=row, ...),
        # ... more lessons
    ])

# Foundation lessons (lesson numbers 2-12)
foundation_lessons = [
    LessonDict(name="2.1: Isolation", algo="repeat", row="focus_e_i", ...),
    # ... 22 foundation lessons
]

LESSONS.extend(foundation_lessons)

# Numbers row lessons (13.1-13.2)
LESSONS.extend([...])

# Keep symbols lessons (14.1-14.3)
LESSONS.extend([...])

# Sentence practice lessons (15.1-15.3)
LESSONS.extend([
    LessonDict(name="15.1: Sentence Practice I", algo="sentence", row="home", ...),
    LessonDict(name="15.2: Sentence Practice II", algo="sentence", row="home", ...),
    LessonDict(name="15.3: Sentence Practice III", algo="sentence", row="home", ...),
])
```

### Step 2: Algorithm Dispatch with Shuffle Logic
**File**: `main.py:1232-1266`
```python
def _generate_physical_keys(self, algo_type: str, row_data: Dict) -> List[PhysicalKey]:
    """Generate physical keys using the specified algorithm."""
    should_shuffle = self.chunks_completed >= self._get_config("SHUFFLE_AFTER")

    # Algorithm strategy pattern
    algorithms = {
        "repeat": lambda: algos.single_key_repeat(
            row_data["left"] + row_data["right"],
            shuffle=should_shuffle,
        ),
        "adjacent": lambda: algos.same_hand_adjacent(
            row_data,
            shuffle=should_shuffle,
        ),
        "alternating": lambda: algos.alternating_pairs(
            row_data,
            shuffle=should_shuffle,
        ),
        "mirror": lambda: algos.mirror_pairs(
            row_data,
            shuffle=should_shuffle,
        ),
        "rolls": lambda: algos.rolls(
            row_data,
            shuffle=should_shuffle,
        ),
        "pseudo": lambda: algos.pseudo_words(row_data),
    }

    generator = algorithms.get(algo_type)
    if generator:
        return generator()
    else:
        # Default: random keys
        all_keys = row_data["left"] + row_data["right"]
        return [random.choice(all_keys) for _ in range(40)]
```

### Step 3: Shift Mode Support
**File**: `main.py:1267-1320`
```python
def _render_keys_to_text(
    self, physical_keys: List[PhysicalKey], shift_mode: str
) -> str:
    """Convert physical keys to text characters with shift mode support."""
    rendered = []

    for key in physical_keys:
        if key == PhysicalKey.KEY_SPACE:
            rendered.append(" ")
            continue

        # Determine if shift should be applied
        apply_shift = False
        if shift_mode == "always":
            apply_shift = True
        elif shift_mode == "mixed":
            apply_shift = random.choice([True, False])  # 50% chance

        # Get character with appropriate shift state
        char = self._get_key_character(key, apply_shift)
        rendered.append(char or "")

    return "".join(rendered)
```

## 4. Content Source Flow: Multi-Source Architecture

### Source A: Local Files
**File**: `sentence_generator.py:51-61`
```python
elif source == "file":
    file_path = Path(get("SENTENCES_FILE"))
    if file_path.exists():
        with open(file_path, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        if lines:
            return normalize_text(random.choice(lines))
```

### Source B: External API
**File**: `sentence_generator.py:37-50`
```python
if source == "api" and HAS_REQUESTS:
    try:
        response = requests.get(get("QUOTE_API_URL"), timeout=2)
        if response.status_code == 200:
            # Adjust parsing based on specific API schema
            data = response.json()
            text = data.get("text", "")
            author = data.get("author")
            if author:
                return normalize_text(f"{text}\n{author}")
            return normalize_text(text)
    except Exception:
        pass
```

### Source C: Command Execution
**File**: `code_generator.py:48-60`
```python
if source == "cmd" and get("CODE_COMMAND"):
    try:
        result = subprocess.check_output(get("CODE_COMMAND"), shell=True, timeout=2)
        text = result.decode("utf-8", errors="ignore").strip()
        if text:
            return normalize_text(text)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass
```

### Source D: AI Generation
**File**: `code_generator.py:61-115`
```python
elif source == "ai":
    api_type = get("AI_API_TYPE")
    endpoint = get("AI_ENDPOINT")
    model = get("AI_MODEL")
    api_key = get("AI_API_KEY")

    if api_type == "auto":
        # Auto-detect API type
        if "localhost" in endpoint or "127.0.0.1" in endpoint:
            api_type = "ollama"
        elif "openai.com" in endpoint:
            api_type = "openai"

    if api_type == "ollama":
        return self._generate_with_ollama(endpoint, model, language)
    elif api_type == "openai":
        return self._generate_with_openai(endpoint, model, api_key, language)
```

## 5. Typing Validation Flow: Enhanced with Code Mode

### Step 1: Key Event Processing with Language Context
**File**: `main.py:265-295`
```python
def on_key(self, event: events.Key) -> None:
    # 1. Identify character
    if event.key == "space":
        char = " "
    elif event.is_printable:
        char = event.character
    else:
        return

    # 2. Map to physical key
    if char == " ":
        physical_pressed = PhysicalKey.KEY_SPACE
    else:
        physical_pressed = self.char_to_physical.get(char)

    # 3. Validate against expected
    idx = len(self.typed_text)
    if idx < len(self.target_keys):
        expected_physical = self.target_keys[idx]

        # Check if physical key matches
        is_correct = False
        if physical_pressed and physical_pressed == expected_physical:
            is_correct = True
        elif char == self.target_text[idx]:  # Fallback
            is_correct = True

        # Handle result
        if is_correct:
            self.typed_text += char
        else:
            self.current_chunk_errors += 1
            if not self._get_config("HARD_MODE"):
                self.typed_text += char
```

### Step 2: Code-Specific Display
**File**: `main.py:332-356`
```python
def refresh_display(self) -> None:
    # ... existing time and stats calculation

    # Add language indicator for code mode
    mode_display = ""
    if self.current_code_language:
        mode_display = f" | LANG: {self.current_code_language.upper()}"

    # Update display with mode info
    display_text = f"{lesson_info} | TIME: {timer_str} | WPM: {wpm} | ACC: {acc}%{mode_display}"
```

## 6. Statistics Calculation Flow: Enhanced with Practice Modes

### Step 1: Real-time WPM Calculation (Unchanged)
**File**: `main.py:332-356`
```python
def refresh_display(self) -> None:
    # Time Calculation
    if self.session_start_time and self.session_active:
        elapsed = time.time() - self.session_start_time
        remaining = max(0, self._get_config("DRILL_DURATION") - elapsed)
    else:
        elapsed = 0
        remaining = self._get_config("DRILL_DURATION")

    # Stats Calculation
    total_chars = self.cumulative_typed_chars + len(self.typed_text)
    total_errs = self.cumulative_errors + self.current_chunk_errors

    safe_elapsed = elapsed if elapsed > 0 else 1e-6
    wpm = round((total_chars / 5) / (safe_elapsed / 60))
    acc = round(((total_chars - total_errs) / max(1, total_chars + total_errs)) * 100)
```

### Step 2: Session Completion with Mode Awareness
**File**: `main.py:478-507`
```python
def evaluate_drill_and_show_stats(self) -> None:
    elapsed = self._get_config("DRILL_DURATION") / 60

    wpm = round((self.cumulative_typed_chars / 5) / elapsed)
    total_ops = self.cumulative_typed_chars + self.cumulative_errors
    acc = round(((self.cumulative_typed_chars - self.cumulative_errors) / max(1, total_ops)) * 100)

    if self.profile:
        # Only check lesson requirements in curriculum mode
        practice_mode = self.profile.config_overrides.get("PRACTICE_MODE", "curriculum")
        if practice_mode == "curriculum":
            lesson = LESSONS[self.profile.current_lesson_index]
            passed = acc >= lesson["target_acc"] and wpm >= lesson["target_wpm"]

            if passed:
                self.profile.current_lesson_index += 1
            else:
                self.notify("Requirements not met. Lesson will repeat.")

        # Always update records
        if wpm > self.profile.wpm_record:
            self.profile.wpm_record = wpm

        self.profile.total_drills += 1
        self.profile.save()
```

## 7. Profile Management Flow: Enhanced Configuration

### Step 1: Profile Creation with Default Overrides
**File**: `models.py:48-70`
```python
@dataclass
class UserProfile:
    name: str
    current_lesson_index: int = 0
    wpm_record: int = 0
    total_drills: int = 0
    level: int = 1
    # Profile-specific overrides for config
    config_overrides: Dict[str, Any] = field(
        default_factory=lambda: INITIAL_PROFILE_OVERRIDES.copy()
    )

    def get_config(self, key: str) -> Any:
        """Get a configuration value, falling back to defaults."""
        return self.config_overrides.get(key, DEFAULT_CONFIG.get(key))

    @property
    def config(self) -> Dict[str, Any]:
        """Get the merged configuration dictionary."""
        merged = DEFAULT_CONFIG.copy()
        merged.update(self.config_overrides)
        return merged
```

### Step 2: Profile Application with Configuration
**File**: `main.py:233-242`
```python
def action_switch_profile(self) -> None:
    def set_profile(profile: UserProfile):
        if profile:
            self.profile = profile
            self.apply_profile_config()  # Apply overrides
            self.notify(f"Welcome, {profile.name}!")
            self.start_new_session()

    self.push_screen(ProfileSelectScreen(), set_profile)
```

## 8. Complete End-to-End Example: Code Practice Mode

### Scenario: User practices Python code snippets

**Step 1: Profile Configuration**
```
User profile config_overrides:
{
    "PRACTICE_MODE": "code",
    "CODE_SOURCE": "local",
    "CODE_LANGUAGES": "python,rust",
    "SHOW_QWERTY": True,
    "SHOW_FINGERS": True
}
```

**Step 2: Practice Text Generation**
```
_get_practice_text() called
practice_mode = "code" (from profile)
languages = ["python", "rust"] (parsed from config)
language = "python" (random choice)
snippet = code_generator.generate_code_snippet("python", profile.config)
Example: "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)"
target_keys = _sentence_to_physical_keys(snippet)
current_code_language = "python"
```

**Step 3: Asynchronous Pre-fetching**
```
_start_prefetching() called in background
Generates next Python snippet while user types current one
Stored in _prefetched_text, _prefetched_keys, _prefetched_language
```

**Step 4: User Typing**
```
User types Python code
on_key() validates each character
refresh_display() shows "LANG: PYTHON" in stats bar
```

**Step 5: Chunk Completion**
```
User completes snippet → check_chunk_completion()
load_next_chunk() uses pre-fetched content
Immediate display of next snippet (no generation delay)
```

**Step 6: Session End**
```
5 minutes elapsed → end_drill_session()
evaluate_drill_and_show_stats()
WPM/accuracy calculated
No lesson requirement check (code mode)
Profile updated with wpm_record and total_drills
```

## 9. Key Data Transformations

### Physical Key → Character (Enhanced)
```
PhysicalKey.KEY_A (value=30)
  → self.resolver.resolve(30, shift=False) → "a"
  → self.resolver.resolve(30, shift=True) → "A"
```

### Character → Physical Key (Enhanced with Shift)
```
Character "A"
  → self.char_to_physical.get("A")
  → Lookup includes both shifted and unshifted mappings
  → PhysicalKey.KEY_A
```

### Algorithm Output Examples (Enhanced)

**`pseudo_words`** (home row, with shift mode):
```
Input: LAYOUT["home"], shift_mode="mixed"
Process: Generate random "words" from home row keys
         Apply shift randomly (50% chance per character)
Output: "asDf jKl; sDFj kL;a"
```

**`sentence` algorithm** (sentence practice):
```
Input: Sentence practice lesson
Process: Call generate_sentence() with profile config
         Source: "api" → fetch from quote API
         Source: "file" → read from sentences.txt
         Source: "local" → use default SENTENCES list
Output: "The quick brown fox jumps over the lazy dog"
```

**Code generation** (Python mode):
```
Input: language="python", source="local"
Process: Read from snippets.py file
         Select random Python function
         Normalize indentation and formatting
Output: "def calculate_average(numbers):\n    total = sum(numbers)\n    return total / len(numbers)"
```

## 10. Configuration Resolution Hierarchy

```
1. Profile config_overrides (highest priority)
   - User-specific customizations
   - Includes INITIAL_PROFILE_OVERRIDES for new profiles
   - Saved in profile.json

2. DEFAULT_CONFIG (models.py)
   - Application-wide defaults
   - Source configurations, API endpoints, file paths
   - Fallback when not in profile overrides

3. Hardcoded config.py values (lowest priority)
   - Fallback when no profile exists
   - Used before profile selection via _get_config()
```

**Note**: `INITIAL_PROFILE_OVERRIDES` are copied into `config_overrides` when a new profile is created,
providing better UX defaults (show keyboard/fingers by default) for new users.

This documentation shows the enhanced flow of data and function calls through the Textype application, with support for multiple practice modes, dynamic content sources, and profile-based configuration.
