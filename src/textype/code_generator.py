"""Code generation algorithms for typing practice.

This module contains algorithms that generate code snippets for different
programming languages (Python, Rust, C, C++) for typing practice.
"""
import random


def generate_code_snippet(language: str = "python") -> str:
    """Generate a random code snippet for typing practice.

    Args:
        language: Programming language for the snippet (python, rust, c, cpp)

    Returns:
        Code snippet as a string

    Raises:
        ValueError: If language is not supported
    """
    language = language.lower()
    if language == "python":
        return _generate_python_snippet()
    elif language == "rust":
        return _generate_rust_snippet()
    elif language == "c":
        return _generate_c_snippet()
    elif language == "cpp":
        return _generate_cpp_snippet()
    else:
        raise ValueError(f"Unsupported language: {language}")


def _generate_python_snippet() -> str:
    """Generate a Python code snippet."""
    snippets = [
        # Class definition with type hints
        "class Point:\n    def __init__(self, x: float, y: float) -> None:\n        self.x = x\n        self.y = y\n\n    def distance(self, other: 'Point') -> float:\n        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5",
        # Function with type hints and default arguments
        "def calculate_total(items: List[float], discount: float = 0.0) -> float:\n    subtotal = sum(items)\n    total = subtotal * (1 - discount)\n    return max(total, 0.0)",
        # Dictionary comprehension
        "squares = {x: x ** 2 for x in range(1, 11)}",
        # Simple if-elif-else
        "def classify_number(n: int) -> str:\n    if n < 0:\n        return 'negative'\n    elif n == 0:\n        return 'zero'\n    else:\n        return 'positive'",
        # Loop with enumerate
        "for index, value in enumerate(['apple', 'banana', 'cherry']):\n    print(f'{index}: {value}')",
        # Try-except block
        "try:\n    result = 10 / divisor\nexcept ZeroDivisionError:\n    result = float('inf')",
        # Data class example
        "from dataclasses import dataclass\n\n@dataclass\nclass User:\n    username: str\n    email: str\n    active: bool = True",
        # Type alias and Union
        "from typing import Union, List\n\nJsonValue = Union[str, int, float, bool, None, List['JsonValue'], Dict[str, 'JsonValue']]",
        # Generator expression
        "even_squares = (x ** 2 for x in range(10) if x % 2 == 0)",
        # String formatting
        "name = 'Alice'\nage = 30\nmessage = f'{name} is {age} years old.'",
    ]
    return random.choice(snippets)


def _generate_rust_snippet() -> str:
    """Generate a Rust code snippet."""
    snippets = [
        # Struct and implementation
        "struct Point {\n    x: f64,\n    y: f64,\n}\n\nimpl Point {\n    fn new(x: f64, y: f64) -> Self {\n        Self { x, y }\n    }\n\n    fn distance(&self, other: &Point) -> f64 {\n        ((self.x - other.x).powi(2) + (self.y - other.y).powi(2)).sqrt()\n    }\n}",
        # Enum with match
        'enum WebEvent {\n    PageLoad,\n    PageUnload,\n    KeyPress(char),\n    Paste(String),\n}\n\nfn inspect(event: WebEvent) {\n    match event {\n        WebEvent::PageLoad => println!("page loaded"),\n        WebEvent::PageUnload => println!("page unloaded"),\n        WebEvent::KeyPress(c) => println!("pressed \'{}\'", c),\n        WebEvent::Paste(s) => println!("pasted \\"{}\\"", s),\n    }\n}',
        # Simple function with pattern matching
        "fn factorial(n: u32) -> u32 {\n    match n {\n        0 => 1,\n        _ => n * factorial(n - 1),\n    }\n}",
        # Vector iteration
        'let numbers = vec![1, 2, 3, 4, 5];\nfor n in numbers.iter() {\n    println!("{}", n);\n}',
        # Option handling
        "fn divide(a: f64, b: f64) -> Option<f64> {\n    if b == 0.0 {\n        None\n    } else {\n        Some(a / b)\n    }\n}",
    ]
    return random.choice(snippets)


def _generate_c_snippet() -> str:
    """Generate a C code snippet."""
    snippets = [
        # Struct and function
        "typedef struct {\n    double x;\n    double y;\n} Point;\n\ndouble distance(Point p1, Point p2) {\n    double dx = p1.x - p2.x;\n    double dy = p1.y - p2.y;\n    return sqrt(dx * dx + dy * dy);\n}",
        # Array iteration
        "int sum_array(int arr[], int size) {\n    int total = 0;\n    for (int i = 0; i < size; i++) {\n        total += arr[i];\n    }\n    return total;\n}",
        # Pointer example
        "void swap(int *a, int *b) {\n    int temp = *a;\n    *a = *b;\n    *b = temp;\n}",
        # Conditional compilation
        '#ifdef DEBUG\n    printf("Debug mode enabled\\n");\n#endif',
        # Enum and switch
        'typedef enum { RED, GREEN, BLUE } Color;\n\nconst char* color_name(Color c) {\n    switch (c) {\n        case RED: return "red";\n        case GREEN: return "green";\n        case BLUE: return "blue";\n        default: return "unknown";\n    }\n}',
    ]
    return random.choice(snippets)


def _generate_cpp_snippet() -> str:
    """Generate a C++ code snippet."""
    snippets = [
        # Class with constructor and methods
        "class Vector {\nprivate:\n    double x, y;\npublic:\n    Vector(double x, double y) : x(x), y(y) {}\n    \n    double magnitude() const {\n        return sqrt(x * x + y * y);\n    }\n    \n    Vector operator+(const Vector& other) const {\n        return Vector(x + other.x, y + other.y);\n    }\n};",
        # Template function
        "template<typename T>\nT max(T a, T b) {\n    return (a > b) ? a : b;\n}",
        # Smart pointer
        "#include <memory>\n#include <vector>\n\nstd::unique_ptr<std::vector<int>> create_vector() {\n    auto vec = std::make_unique<std::vector<int>>();\n    vec->push_back(1);\n    vec->push_back(2);\n    return vec;\n}",
        # Lambda expression
        "auto add = [](int a, int b) { return a + b; };\nint result = add(5, 3);",
        # Namespace usage
        "namespace geometry {\n    const double PI = 3.141592653589793;\n    \n    double circle_area(double radius) {\n        return PI * radius * radius;\n    }\n}",
    ]
    return random.choice(snippets)


if __name__ == "__main__":
    print("Python snippet:")
    print(generate_code_snippet("python"))
    print("\nRust snippet:")
    print(generate_code_snippet("rust"))
    print("\nC snippet:")
    print(generate_code_snippet("c"))
    print("\nC++ snippet:")
    print(generate_code_snippet("cpp"))
