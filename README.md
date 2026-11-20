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

| Parameter | Default | Description |
| --- | --- | --- |
| Context size | `0` (model's training context) | Tokens available for prompt and response; larger contexts use more memory. |
| 8-bit KV cache | Enabled | Quantizes both key and value caches to `q8_0`, reducing cache memory use with a possible quality trade-off. Enter `n` to use the runtime defaults. |
| Top-k | `40` | Limits choices to the k most likely next tokens; `0` disables it. |
| Top-p | `0.95` | Keeps the most likely tokens up to a cumulative probability of p; lower values restrict choices. |
| Temperature | `0.8` | Higher values increase randomness; `0` chooses the most likely token. |
| Min-p | `0.05` | Excludes tokens below this fraction of the most likely token's probability; `0` disables it. |
| Repetition penalty | `1.0` | Values above `1` discourage repeated tokens; `1` disables it. |
| Maximum generated tokens | `-1` (unlimited) | Limits response length, except in `--cli` mode. |

### Notes
1. The context selected by `0` can require substantial memory.
1. 8-bit KV cache support depends on the model and runtime backend. Disable it if the generated llamafile cannot initialize the cache.
1. In llamafile 0.10.6, `--cli` mode ignores the maximum generated tokens setting.
1. Windows cannot run llamafile executables larger than 4 GB.

See the upstream [creating llamafiles guide](https://docs.mozilla.ai/llamafile/using-llamafile/creating_llamafiles)
for details.
