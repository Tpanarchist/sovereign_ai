from typing import Callable, Dict
from ..memory.memory_engine import save_event
from pathlib import Path
import subprocess
import shlex  # For improved command parsing

class RitualCompiler:
    def __init__(self):
        self.registry: Dict[str, Callable[[str], str]] = {}

    def register(self, tag: str, action: Callable[[str], str]):
        self.registry[tag.lower()] = action

    def invoke(self, tag: str, payload: str) -> str:
        tag_key = tag.lower()
        if tag_key not in self.registry:
            return f"[Error] No ritual registered for tag: {tag}"
        try:
            result = self.registry[tag_key](payload)
            save_event({
                "tag": f"Invocation:{tag}",
                "content": f"Payload: {payload} → Result: {result}"
            })
            return result
        except Exception as e:
            return f"[Error] Ritual '{tag}' failed: {str(e)}"

# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃              [RITUAL INVOCATIONS]          ┃
# ┃  Functions Sov may call to affect reality  ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

def search_web(query: str) -> str:
    return f"[Simulation] Would search the web for: '{query}'"

def write_file(command: str) -> str:
    try:
        import shlex
        print(f"[DEBUG] write_file invoked with: {command}")  # LOG HERE
        parts = shlex.split(command)
        if len(parts) < 2:
            return "[Error] Usage: [Invocation: write_file path content...]"
        path = parts[0]
        content = " ".join(parts[1:])
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"[Success] File '{path}' written successfully."
    except Exception as e:
        return f"[Error] Writing file failed: {str(e)}"

def edit_file(command: str) -> str:
    try:
        parts = command.split(" ", 4)
        if len(parts) < 5:
            return "[Error] Usage: [Invocation: edit_file] <path> <mode> <line> <text>"

        _, path, mode, line_str, text = parts
        line = int(line_str)
        p = Path(path)

        if not p.exists():
            return f"[Error] File '{path}' not found."

        lines = p.read_text(encoding="utf-8").splitlines()
        if mode == "replace":
            lines[line] = text
        elif mode == "insert":
            lines.insert(line, text)
        else:
            return f"[Error] Invalid mode: {mode}"

        p.write_text("\n".join(lines), encoding="utf-8")
        return f"[Success] File '{path}' updated at line {line} via {mode}."
    except Exception as e:
        return f"[Error] Failed to edit file: {str(e)}"

def run_file(command: str) -> str:
    try:
        # Use shlex to properly handle the command
        parts = shlex.split(command)
        path = parts[0] if len(parts) > 0 else command
        
        # Execute without any security checks or restrictions
        result = subprocess.run(["python", path], capture_output=True, text=True, shell=False)
        output = result.stdout + result.stderr
        return f"[Executed: {path}]\n{output}"
    except Exception as e:
        return f"[Error] Failed to run file: {str(e)}"

def reflect_memory(_: str) -> str:
    from ..memory.memory_engine import summarize_memory
    return "[Reflection] " + summarize_memory()

def add_custom_ritual(code: str) -> str:
    ritual_path = Path(__file__)
    with open(ritual_path, "a", encoding="utf-8") as f:
        f.write("\n\n# [User Ritual]\n" + code + "\n")
    return "[Invocation] Ritual added to compiler. Reload required to take effect."