Image deduplication app
====


About
----

Image deduplicate script and GTK app to compare.

[![Python 3.13](https://img.shields.io/badge/python-3.13-green.svg)](https://www.python.org/downloads/release/python-3136/)
[![Code style: ruff](https://img.shields.io/badge/ruff-enabled-informational?logo=ruff)](https://astral.sh/ruff)
[![License](https://img.shields.io/badge/license-BSD-blue.svg)](https://raw.githubusercontent.com/manti-by/pdw/master/LICENSE)

Author: Alexander Chaika <manti.by@gmail.com>

Source link: https://github.com/manti-by/mgallery/

Rust mirror: https://github.com/manti-by/mgallery-rust/

Requirements:

    Python 3.13, OpenCV, Redis, GTK


Script setup
----

1. Set appropriate environment variables:

    ```bash
    export REDIS_URL=redis://127.0.0.1:6379/5
    export GALLERY_PATH=/home/ubuntu/app/data/
    export DEBUG_LOG=/tmp/mgallery/debug.log
    export ERROR_LOG=/tmp/mgallery/error.log
    ```

2. Install necessary libraries

    ```bash
    sudo apt install -y pkg-config python3-dev libraw-dev
    sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 libgirepository1.0-dev gcc libcairo2-dev
    ```

3. Setup environment and install packages from requirements file:

    ```bash
    pip3 install -r requirements.txt
    ```
   
4. Scan a gallery and compare duplicates

   ```bash
   make setup
   make scan
   make compare
   ```

Image tagging
----

The `-p` flag sends a local image to a locally running Ollama vision model
(default `gemma3:12b`) and prints a normalized JSON list of tags to stdout.
The model is queried via the [`ollama`](https://github.com/ollama/ollama-python)
Python client with `format="json"` and a low temperature for stable output.
Tags are lowercased, trimmed, deduplicated, and capped at 20 entries.

Requirements:

- A running Ollama daemon with the `gemma3:12b` model pulled locally:
  ```bash
  ollama serve &
  ollama pull gemma3:12b
  ```

Environment variables:

- `OLLAMA_HOST` (default `http://localhost:11434`) — Ollama API base URL.
- `OLLAMA_MODEL` (default `gemma3:12b`) — vision model to use.

Examples:

```bash
# Tag a single image with the default model
uv run mgallery.py -p /path/to/photo.jpg

# Override the model
uv run mgallery.py -p /path/to/photo.jpg -m llama3.2-vision:11b
```

Sample output (machine-readable JSON, ready to pipe into another tool):

```json
{"tags": ["sunset", "beach", "sea", "orange sky", "horizon"]}
```

The script fails with a clear error message on stderr and a non-zero exit
code when:

- the image file does not exist;
- Ollama is not running at `OLLAMA_HOST`;
- the requested model is not installed locally;
- the model returns a response that cannot be parsed as the expected JSON.
