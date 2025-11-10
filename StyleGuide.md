# Style Guide
*Style guide for our Rosette Identification Project*

## Comment style
### Function comments
- All functions will have a block comment inside the header of the function that specifies what the function does
    - Exmaple:
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

### Inline comments
- Use inline comments to explain non-obvious logic in the code
- Place inline comments on its own line above the relavent code
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

Like naming conventions for variables and class, branch names should be clear and concise.

This is also the default branch naming style in Github if you create a branch off an issue, with the feature name being the name of the issue.

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
- Add or update unit tests alongside code changes.
- Maintain or improve test coverage for touched areas.


## Coupling & Cohesion
We will follow [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) coding principles and [SOLID](https://en.wikipedia.org/wiki/SOLID) for any object-oriented design in this project

## Other References
[Google Style Guide](https://google.github.io/styleguide/)
[Python PEP 8](https://peps.python.org/pep-0008/)
