PROJECT SUMMARY


This project represents the most structured and realistic software-engineering workflow I have completed so far. Instead of simply writing code, I developed the system using a full AI-assisted engineering pipeline powered by Spec-Kit, GitHub Copilot, ChatGPT, automated tests, and generated planning documents. The result is a complete task manager application with specifications, tests, a CLI, and a clean commit history showing every step of the process.

1. Using Spec-Kit to Generate an Engineering Workflow

The development began with Spec-Kit, which generated the entire project blueprint. The tool created a Constitution, which defined the high-level purpose of the system, design principles, constraints (JSON storage, no database, predictable behavior), and user interaction philosophy. It then generated the Plan, describing the data model, storage logic, CLI structure, and expected behaviors. Finally, it created Tasks, which broke the system down into small actionable developer steps.

This workflow was extremely helpful because it forced me to think like an engineer working in a real team where planning comes before coding. It also gave me a roadmap showing exactly what to implement and how the parts fit together.

2. Using AI Coding Assistance
ChatGPT (Chat-based reasoning and debugging)

Throughout the process, ChatGPT was my main tool for understanding errors, interpreting planning documents, and resolving environment issues.
It helped me solve:

Hardlink failures during Spec-Kit installation

Missing pytest and dev dependencies

Wrong package paths causing “ModuleNotFoundError: taskmgr”

Windows path confusion between OneDrive, Desktop, and Project directories

uv and venv issues

Fixing the editable install (pip install -e .) so pytest and the CLI worked correctly

Every time I encountered a blocker, ChatGPT explained the cause and walked me through a fix.

GitHub Copilot (autocomplete + inline coding assistance)

I used Copilot for:

Generating helper functions

Writing repeated patterns in CLI code

Filling in docstrings

Suggesting improvements to loops and storage logic

Assisting with parts of the test suite

Copilot was very helpful for speed, but it also made incorrect suggestions—especially when it tried to “guess” specifications incorrectly. I had to constantly compare its suggestions to the official Spec-Kit Plan. This taught me that Copilot is a strong assistant, not a replacement for understanding the design.

Spec-Kit Agents

Spec-Kit was the most structured AI tool out of all of them. It created:

The Constitution file

Detailed Plan

Full Tasks list

Auto-generated reference implementation files

Unit tests for the storage module

A consistent folder layout

This gave me a blueprint similar to what a tech lead or architect would normally create.

3. What Worked Well

Automated tests:
Running pytest immediately exposed bugs in my storage logic before I continued development. The atomic write tests especially helped me fix JSON save behavior.

Editable install (pip install -e .):
Once I set this up correctly, everything “clicked.” The CLI worked properly, and the module became importable during tests.

Spec-Kit templates:
These forced me into a professional workflow instead of coding randomly. The structure made the project easier to reason about.

Combining AI tools:
ChatGPT solved conceptual and environment problems. Copilot handled repetitive coding. Spec-Kit produced specifications and structure. Together, they massively accelerated development.

4. What Did Not Work / False Starts

I initially installed Spec-Kit incorrectly due to Windows hardlink errors.

I kept running pytest from the wrong folder because OneDrive created multiple paths.

I forgot to add pytest to dev dependencies in an earlier task, which caused missing command errors.

Copilot sometimes hallucinated functions not in the specification.

Running scripts outside the virtual environment produced confusing import errors.

I mistakenly tried running python -m taskmgr before installing the package in editable mode.

Each mistake forced me to slow down, understand my environment, and reread the Spec-Kit plan.

5. Final Reflection

This project taught me how real engineering workflows operate: specification → planning → tasks → implementation → tests → documentation. More importantly, it showed me how to use AI responsibly—leveraging its strengths while verifying its output. The final product is a fully working task manager backed by a professional-style development pipeline.
