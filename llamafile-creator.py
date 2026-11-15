#!/usr/bin/env python3
import math
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import urllib.request


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT / "workspace"
GGUFS = ROOT / "ggufs"
RELEASE = "https://github.com/mozilla-ai/llamafile/releases/download/0.10.6"


def download(name, temporary):
    destination = WORKSPACE / (name + (".exe" if os.name == "nt" else ""))
    if not destination.exists():
        print(f"Downloading {name}...", flush=True)
        partial = temporary / destination.name
        urllib.request.urlretrieve(f"{RELEASE}/{name}", partial)
        partial.replace(destination)
    destination.chmod(destination.stat().st_mode | 0o111)
    return destination


def number(label, default, kind, minimum, maximum=None):
    value = kind(input(f"{label} [{default}]: ").strip() or default)
    if (kind is float and not math.isfinite(value)) or value < minimum or (
        maximum is not None and value > maximum
    ):
        raise ValueError(f"Invalid {label}: {value}")
    return str(value)


def main():
    WORKSPACE.mkdir(exist_ok=True)
    GGUFS.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory(dir=WORKSPACE) as directory:
        temporary = Path(directory)
        runtime = download("llamafile-0.10.6", temporary)
        zipalign = download("zipalign-0.10.6", temporary)

        models = sorted(
            (path for path in GGUFS.iterdir() if path.is_file() and path.suffix.lower() == ".gguf"),
            key=lambda path: path.name.lower(),
        )
        if not models:
            raise ValueError(f"No .gguf files found in {GGUFS}")
        for index, model in enumerate(models, 1):
            print(f"{index}. {model.name}")
        selection = int(input("Choose a model: "))
        if not 1 <= selection <= len(models):
            raise ValueError("Invalid model selection")
        model = models[selection - 1]
        if any(ord(char) < 32 or ord(char) == 127 for char in model.name):
            raise ValueError("Model filename must not contain control characters")

        print("\nPress Enter to use each default.")
        print("Context size: tokens available for the prompt and response; larger values use more memory.")
        context = number("Context size (0 = model default)", "0", int, 0, 2**31 - 1)
        print("Top-k: consider only the k most likely next tokens; lower values restrict choices (0 disables).")
        top_k = number("Top-k", "40", int, 0, 2**31 - 1)
        print("Top-p: keep the most likely tokens whose probabilities add up to p; lower values restrict choices.")
        top_p = number("Top-p", "0.95", float, 0, 1)
        print("Temperature: higher values increase randomness; 0 chooses the most likely token.")
        temperature = number("Temperature", "0.8", float, 0)
        print("Min-p: exclude tokens below this fraction of the most likely token's probability; 0 disables.")
        min_p = number("Min-p", "0.05", float, 0, 1)
        print("Repetition penalty: values above 1 discourage repeated tokens; 1 disables the penalty.")
        repeat_penalty = number("Repetition penalty", "1.0", float, 0)
        if float(repeat_penalty) == 0:
            raise ValueError("Repetition penalty must be greater than zero")
        print("Maximum generated tokens: limit response length; --cli mode ignores this setting in 0.10.6.")
        max_tokens = number("Maximum generated tokens (-1 = unlimited)", "-1", int, -1, 2**31 - 1)

        suffix = input("Suffix: ").strip()
        if not suffix or any(char in '/\\' or ord(char) < 32 or ord(char) == 127 for char in suffix):
            raise ValueError("Suffix must be non-empty and cannot contain path separators or control characters")

        args = temporary / ".args"
        args.write_text(
            "\n".join(
                [
                    "-m", shlex.quote(f"/zip/{model.name}"),
                    "-c", context,
                    "--top-k", top_k,
                    "--top-p", top_p,
                    "--temp", temperature,
                    "--min-p", min_p,
                    "--repeat-penalty", repeat_penalty,
                    "-n", max_tokens,
                    "...",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        name = f"{model.stem}_{suffix}.llamafile"
        output = WORKSPACE / name
        building = temporary / name
        shutil.copy2(runtime, building)
        print(f"Creating {output}...", flush=True)
        command = [str(zipalign), "-j0", str(building), str(model), str(args)]
        if os.name != "nt":
            command.insert(0, "/bin/sh")
        subprocess.run(command, check=True)
        building.chmod(building.stat().st_mode | 0o111)
        building.replace(output)
        print(f"Created {output}")


if __name__ == "__main__":
    try:
        main()
    except EOFError:
        print("Error: input ended unexpectedly", file=sys.stderr)
        sys.exit(1)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
