import ast, os, sys

errors = []
root = "streamlit_app"
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d != "venv"]
    for filename in filenames:
        if filename.endswith(".py"):
            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, encoding="utf-8") as f:
                    source = f.read()
                ast.parse(source)
                print(f"  OK  {filepath}")
            except SyntaxError as e:
                print(f"  ERR {filepath}: {e}")
                errors.append(filepath)

print()
if errors:
    print(f"FAILED: {len(errors)} file(s) have syntax errors")
    sys.exit(1)
else:
    print(f"All Python files are syntactically valid!")
