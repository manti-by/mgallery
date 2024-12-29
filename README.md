Image deduplication app
====


About
----

Image deduplicate script and GTK app to compare.

[![Python 3.12](https://img.shields.io/badge/python-3.12-green.svg)](https://www.python.org/downloads/release/python-3111/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License](https://img.shields.io/badge/license-BSD-blue.svg)](https://raw.githubusercontent.com/manti-by/mgallery/master/LICENSE)

Author: Alexander Chaika <manti.by@gmail.com>

Source link: https://github.com/manti-by/mgallery/

Rust mirror: https://github.com/manti-by/mgallery-rust/

Requirements:

    Python 3.12, OpenCV, Redis, GTK


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
