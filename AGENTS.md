# Repository Guidelines

## Project Structure

- `Week_03_Prompting/` contains prompting assignments, restaurant datasets under `Assignments/Task_2/data/`, and Python experiment scripts and tests in `week03_starter/`.
- `Week_04_Requirements/` holds requirements exercises and source material in `Task_1/data/corpus/`. `Week_05_Designing/` contains design exercises in `Tasks/` and RecipeCove architecture decision records in `RecipeCove/`.
- `Week_06_Implementation/rag/` contains retrieval and generation scripts, tests, and JSON artifacts. The sample Python package and its tests live under `Week_06_Implementation/AI4SE_Playground/playground/`.
- `Week_08_Dissecting/Assignments/` groups agent exercises by task. Keep reports and screenshots beside the task they document.

## Development and Testing

Run these commands from the repository root. Each lab has its own entry points.

- With a Python virtual environment active, run `python3 -m pip install -r Week_06_Implementation/rag/requirements.txt` to install the RAG dependencies.
- `(cd Week_03_Prompting/week03_starter && python3 -m unittest -v test_solution.py)` checks prompt handling and analysis offline.
- `python3 -m unittest discover -s Week_06_Implementation/rag` checks retrieval and generation with local artifacts and mocked API calls.
- `(cd Week_06_Implementation/AI4SE_Playground/playground && python3 -m unittest discover -s tests)` runs the sample package suite.

Use `unittest` with `test_*.py` files and descriptive `test_*` methods. Cover changed behavior with focused checks and mock external API calls. Read the relevant assignment before running live experiments. Supply `OPENAI_API_KEY` through the environment for live RAG calls and keep credentials out of commits.

## Coding Style and Naming

Use four spaces for Python indentation, `snake_case` for functions and modules, and `PascalCase` for classes. Follow the adjacent files when naming task reports and ADR revisions. Preserve relative links when moving reports or assets.

## Commits and Pull Requests

Use short, descriptive subjects that identify the week or task when helpful, such as “Complete Week 6 RAG assignments.” In the pull request, identify the affected tasks, summarize the changes, and list verification commands or results. Link the relevant assignment or issue and attach screenshots when they provide evidence for the exercise.
