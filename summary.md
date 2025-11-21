Summary of My Development Process

For this project, I built a full task-manager application by following a structured, AI-assisted development workflow using GitHub Spec-Kit, ChatGPT, and GitHub Copilot. This project required not only writing code, but also generating specifications, tests, documentation, and a complete development history. This summary explains how I used different AI tools, what worked well, what issues I ran into, and how the final version of the software was produced.

Using AI Tools and Workflows
1. Starting With Spec-Kit (the “Constitution → Plan → Specs → Tasks → Implement” pipeline)

The development process began by creating a brand-new repository for the task manager and initializing it with Spec-Kit. I used uvx specify init . to generate the project structure and select GitHub Copilot as the AI assistant. Spec-Kit then guided me through several structured steps:

/speckit.constitution – I created a constitution describing goals, design principles, constraints, and philosophies for the task-manager system.

/speckit.plan – Spec-Kit generated the technical plan and created Phase 1 artifacts including data-model.md, cli.md, and quickstart.md.

/speckit.specify – This produced the functional specification with clearer requirements.

/speckit.tasks – This generated checklist-style development tasks and established a dependency-ordered build plan.

/speckit.implement – Finally, Spec-Kit scaffolded the reference implementation (CLI, storage system, and tests).

This pipeline worked extremely well because it forced a disciplined, structured approach that mirrored real-world software engineering practices.

2. Using ChatGPT for Debugging, Environment Issues, and Guidance

ChatGPT played a major role throughout development, especially when things went wrong. Some examples include:

Environment issues caused by OneDrive hardlink errors when installing Spec-Kit. ChatGPT helped me fix this by setting UV_NO_HARDLINKS=1.

PowerShell not supporting bash commands required by Spec-Kit. ChatGPT explained how to emulate the script manually.

pytest failing because the package wasn’t on the Python path. ChatGPT guided me to add a minimal pyproject.toml and install the project in editable mode (pip install -e .).

Fixing import errors like import taskmgr not being recognized.

Ensuring dev dependencies (like pytest) were added properly so the grader wouldn’t deduct points, as happened in Task 3.

Helping generate additional tests, explanations, and clarifications for anything unclear in the specs.

Overall, ChatGPT was the “software engineer partner” throughout this whole project.

3. Using GitHub Copilot (Inline + Chat Modes)

Copilot helped inside VS Code by:

Autocompleting Python functions inside the CLI and storage modules.

Suggesting fixes to path issues, JSON handling, and test implementations.

Filling in missing docstrings and usage examples.

Helping rewrite parts of the implementation to match the generated specification.

I used both inline Copilot suggestions and the Copilot Chat sidebar to refine code, especially inside the taskmgr/ modules.

What Worked Well

Spec-Kit’s structured workflow removed guesswork and made development feel like following a real engineering blueprint.

ChatGPT’s explanations made environment issues easy to solve.

Copilot sped up coding inside the editor.

Pytest integration ensured correctness and caught errors early.

The final software ended up clean, modular, and fully tested.

What Didn’t Work / False Starts

Windows PowerShell caused many issues (no bash, path errors, “the term is not recognized”).

OneDrive’s syncing prevented hardlink creation and broke installations.

Missing dev dependencies in earlier tasks taught me to always include them.

Errors where Spec-Kit scripts expected a UNIX-like shell forced manual fixes.

Initially I tried to run the implementation before installing the project in editable mode, which broke imports.

Despite these issues, every problem was eventually resolved through AI guidance.

Final Result

The final software includes:

A working Python CLI task manager

A full specification and plan

Automated tests

Documentation and prototypes

A clean commit history

And a 6–8 minute demonstration video linked in video.txt

This project helped me understand structured AI-assisted software development in a real engineering workflow.
