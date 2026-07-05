🦎 Flex Programming Language
"Programming should feel as smooth as chatting with your friends."
Flex is a high-level, expressive, systems-friendly programming language designed to strip away traditional syntax noise (semicolons, heavy braces, boilerplate imports) and replace it with intuitive, natural British English structures.
It is engineered specifically for students, educators, and modern developers who value speed, clean readability, and a delightful debugging experience. Under the hood, Flex features its own custom Lexer, Parser, Semantic Analyzer, and direct Execution Engine.
🎨 Visual Architecture
               FLEX ARCHITECTURE
               
       +──────────────────────────────+
       │    Source File (app.flex)     │
       +──────────────┬───────────────+
                      │
                      ▼
       +──────────────────────────────+
       │    Lexical Scanner (Lexer)   │  ◄── Catches spelling errors
       +──────────────┬───────────────+      (e.g., "color" -> "colour")
                      │
                      ▼
       +──────────────────────────────+
       │   Syntactic Parser (AST)     │  ◄── Builds execution tree
       +──────────────┬───────────────+
                      │
                      ▼
       +──────────────────────────────+
       │      Semantic Analyzer       │  ◄── Friendly scope resolution
       +──────────────┬───────────────+      suggesting closest variables
                      │
                      ▼
       +──────────────────────────────+
       │      Interpreter Runtime     │  ◄── Zero-dependency execution
       +──────────────────────────────+


✨ Key Features
British English Native: Clean commands (programme, initialise, constant, colour).
Friendly Debugging ("Vibe Checks"): Rejects cryptographic memory dumps. Tells you exactly what is wrong using modern, polite, and constructive micro-copy.
Zero-Boilerplate Setup: Variables, blocks, and conditions flow naturally without brackets or semicolon overhead.
Ecosystem Ready: Built-in command line interface (CLI) to easily initialize and run projects.
🚀 Quick Start
1. Prerequisites
Flex is written in python with zero external dependencies, making it highly portable. Ensure you have Python 3.8+ installed.
2. File Structure
Initialize your project using the following structure:
MyProject/
├── flex.toml
└── src/
    └── main.flex


3. Running Code
To execute your Flex code, run:
python compiler/flex.py run src/main.flex


🛠️ Syntax Overview
Here is how clean and elegant a standard program looks in Flex:
programme WelcomeSystem {
    initialise studentName = "Bhanu"
    constant passingGrade = 75
    initialise score = 85

    display "Checking credentials..."

    if (score >= passingGrade) {
        spill "Vibe Check Passed: Well done " + studentName
    } else {
        spill "Keep training, you've got this!"
    }
}


⚙️ Development Roadmap
[x] Functional Lexer & Recursive Parser
[x] Scope-Checking Semantic Analyzer
[x] Real
