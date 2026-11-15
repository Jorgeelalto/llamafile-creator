# llamafile-creator

Create a self-contained llamafile from a local language-model GGUF.

## Usage

Install [uv](https://docs.astral.sh/uv/), put one or more `.gguf` files in
`ggufs/` next to the script, and run:

```sh
uv run llamafile-creator.py
```

Put the model in `.gguf` format that you want to use in `ggufs/`. The script will
create the `workspace/` folder and do its things there, and will download tooling
if required. It will also prompt you for llamafile arguments, although you can just
use the defaults:

| Parameter | Default |
| --- | --- |
| Context size | `0` (model's training context) |
| Top-k | `40` |
| Top-p | `0.95` |
| Temperature | `0.8` |
| Min-p | `0.05` |
| Repetition penalty | `1.0` |
| Maximum generated tokens | `-1` (unlimited) |

### Notes
1. The context selected by `0` can require substantial memory.
1. In llamafile 0.10.6, `--cli` mode ignores the maximum generated tokens setting.
1. Windows cannot run llamafile executables larger than 4 GB.

See the upstream [creating llamafiles guide](https://docs.mozilla.ai/llamafile/using-llamafile/creating_llamafiles)
for details.
