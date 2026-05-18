# Contributing Guidelines for Project AEDES UIF

## 1. **Getting Started**:
- **Fork the Repository**: Start by forking the `aedesproject-uif` repository to your own GitHub account. If you're unfamiliar with this process, [here's a tutorial on forking](https://docs.github.com/en/get-started/quickstart/fork-a-repo).
- **Clone the Forked Repository**: Clone your forked repository to your local machine using `git clone https://github.com/Cirrolytix/aedesproject-uif/`. This allows you to make changes without affecting the main project.

## 2. **Setting Up Your Environment**:
- **Virtual Environment**: Before installing any packages, set up a virtual environment to avoid package conflicts. You can use tools like `virtualenv` or the built-in `venv` module. [Here's a guide to help you set it up](https://docs.python.org/3/tutorial/venv.html).
- Install the required packages using `pip install -r requirements.txt`.

## 3. **Making Changes**:
- **Open an Issue**: Before starting significant changes or new features, open an issue to discuss your ideas. This ensures alignment with the project's goals and can save both your time and the maintainers'.
- **Create a New Branch**: Always create a new branch for your changes. This keeps the master branch clean and release-ready.
- **Follow the Code Style**: Adhere to the Python PEP 8 style guide. Consider using tools like `flake8`, `black`, or `isort` to maintain consistent code formatting.
- **Write Tests**: Ensure you write tests to cover your changes.
- **Document Your Changes**: Update the README or other documentation to reflect any new features or important modifications.

## 4. **Committing and Pushing Your Changes**:
- Make atomic commits, where each commit represents a single logical change.
- Write clear and concise commit messages that explain your changes.
- Push your changes to your forked repository on GitHub.

## 5. **Submitting a Pull Request (PR)**:
- Once you've pushed your changes, go to the main `aedesproject-uif` repository and click on "New Pull Request".
- Choose the branch from your forked repository that contains your changes.
- Fill out the provided PR template, describing your changes in detail and linking any related issues.
- Ensure the Continuous Integration (CI) checks pass. Address any failures before requesting a review.

## 6. **Naming and Labeling Conventions**:

- **Branch Naming**:
  - Use concise, descriptive names.
  - Prefix feature branches with `feature/`, bug fixes with `bugfix/`, and hotfixes with `hotfix/`. For example: `feature/new-ui-component` or `bugfix/login-issue`.

- **Commit Messages**:
  - Start with a capital letter and use present tense, e.g., "Add new feature" instead of "Added new feature" or "adds new feature".
  - Keep messages concise but descriptive enough to understand the change at a glance.

- **PR Titles**:
  - Like commit messages, use present tense and be descriptive.
  - If the PR closes an issue, reference it in the title, e.g., "Fix login bug - closes #123".

- **Issue Labels**:
  - Use consistent colors and naming for labels.
  - Common labels include:
    - `bug`: For bug reports.
    - `feature`: For new features or enhancements.
    - `documentation`: For updates related to documentation.
    - `question`: For questions or discussions.
    - `help wanted`: For tasks that need assistance.
    - `good first issue`: For tasks suitable for newcomers.
  - Use labels to indicate priority: `low-priority`, `medium-priority`, `high-priority`.

- **Variable and Function Naming (Python Code)**:
  - Use `snake_case` for variable and function names, e.g., `calculate_average()`.
  - Use `CamelCase` for class names, e.g., `DataProcessor`.
  - Be descriptive with names. Instead of `proc_data()`, use `process_data()`.

- **File and Directory Naming**:
  - Use lowercase letters and separate words with underscores, e.g., `user_data.py`.
  - Organize related files within directories, e.g., all UI components might go in a `ui_components` directory.

- **Tagging Releases**:
  - Use [Semantic Versioning](https://semver.org/), e.g., `v1.2.3`.
  - Prefix tags with a `v`, followed by the version number.

## 7. **Review Process**:
- Your PR will be reviewed within a week. If it takes longer, feel free to ping the maintainers or ask for an update.
- Address any feedback or concerns raised during the review. This might involve making more changes and updating your PR.

## 8. **Community Interaction**:
- Be respectful and considerate of others. Engage in constructive discussions and be open to feedback.
- Always refer back to the project's [Code of Conduct](CODE_OF_CONDUCT.md) to ensure you're aligned with the expected behaviors.

## 9. **Recognition**:
- Contributors are invaluable to the project. Your contributions will be acknowledged in a dedicated "Contributors" section in the README or a separate CONTRIBUTORS file.

## 10. **Stay Updated**:
- Regularly pull changes from the main `aedesproject-uif` repository to stay updated. If you're unfamiliar with syncing forks, [here's a guide to help you](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork).


