# Learning Concepts

## Step 1.2: Git Change Detection ✅

### What We Learned

**1. Python subprocess Module**
```python
subprocess.run(["git", "diff", "--name-only"], 
               capture_output=True,  # Capture stdout/stderr
               text=True,            # Return string not bytes
               check=True)          # Raise exception on error
```

**Key Concepts**:
- `subprocess.run()` executes shell commands
- `capture_output=True` captures command output
- `text=True` converts bytes to string
- `check=True` raises exception if command fails

**2. Error Handling**
```python
try:
    result = subprocess.run(...)
except subprocess.CalledProcessError:
    # Handle git errors gracefully
except FileNotFoundError:
    # Handle missing git
```

**3. String Processing**
```python
files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
```
- Split by newline
- Strip whitespace
- Filter empty strings
- List comprehension

### Git Commands Used

- `git diff --name-only HEAD~1` - List changed files vs previous commit
- Returns only filenames, not full diff

### Next: Step 1.3 - Pattern Matching

We'll learn:
- Glob patterns (`*.py`, `src/**/*.js`)
- `fnmatch` module
- Pattern matching algorithms
