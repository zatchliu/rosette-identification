# Style Guide
*Style guide for our Rosette Identification Project*

## Comment style
### Function comments
- All functions will have a block comment inside the header of the function that specifies what the function does
    - Example:
    ```
    def foo(bar):
        """
        This is an example of a function comment!
        Args: 
            bar
        Returns:
            None
        """
        return None
    ```

    **Note:** For this project, we don't need to strictly follow this format for the function comments (including Args, Returns, etc), as long as there is a sufficient description of the function

### Inline comments
- Use inline comments to explain non-obvious logic in the code
- Place inline comments on their own line above the relevant code
    - Example: 
    ```
    # This is an inline comment!
    print("Hello world!")
    ```

## Naming conventions
Variable, function, and class names should be clear and concise. A longer, more descriptive name is better than a short and unclear one.

### Name Casing

**Variables and Functions**: `snake_case`

**Classes**: `CamelCase` (note class names should be capitalized)

**Constants and Global Variables**: `UPPER_SNAKE_CASE`

## Branching
### Branch Names
Branch names should adhere to the following format: **ISSUE_NUMBER-FEATURE_NAME**
Example:
`1-image-input-and-preprocessing`

Like naming conventions for variables and classes, branch names should be clear and concise.

This is also the default branch naming style in GitHub if you create a branch off an issue, with the feature name being the name of the issue.

### Branch Creation Norms
- Create a new branch for each independent feature or substantial change.
- Base new branches off `main` unless coordinating off another active feature explicitly.
- Keep branches focused and short-lived; prefer multiple small PRs over one very large PR.

### Commit Message Norms
- Write clear, imperative commit messages. Make sure to include context when helpful.

### Pull Request and Merge Conditions
- Open a PR from your feature branch into `main` when the feature is complete.
- Requirements to merge:
  - All checks pass (formatting, linting, tests).
  - At least one reviewer approval.
  - No unresolved review comments.
  - Branch is up-to-date with `main`

### Testing Norms
- Testing is done with visual output.
- There are no annotated cell images to officially test "correctness" with, so visual testing is the best option currently.

## HTML/JavaScript Code Style

The interactive visualization uses embedded HTML/JavaScript in `src/rosette_detection.py`.

**JavaScript:**
- Use `const` and `let` (no `var`)
- camelCase for variables and functions
- Add descriptive comments for complex functions
- Keep functions focused on single tasks

**HTML/CSS:**
- Use semantic HTML5 elements
- Semantic class/id names
- Group related CSS properties


## Coupling & Cohesion
We will follow [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) coding principles and [SOLID](https://en.wikipedia.org/wiki/SOLID) for any object-oriented design in this project

## Other References
[Google Style Guide](https://google.github.io/styleguide/)
[Python PEP 8](https://peps.python.org/pep-0008/)
