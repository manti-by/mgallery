install:
	sudo apt install -y pkg-config python3-dev libraw-dev
	sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 libgirepository-2.0-dev gcc libcairo2-dev

flush-db:
	redis-cli -n 5 FLUSHALL

clean-dirs:
	rm -rf /var/mgallery/thumbnails/*
	rm -rf /var/log/mgallery/*

make-dirs:
	sudo mkdir -p /var/mgallery/thumbnails && \
	sudo chown manti:manti /var/mgallery/thumbnails && \
	sudo mkdir -p /var/log/mgallery && \
	sudo chown manti:manti /var/log/mgallery

setup: flush-db clean-dirs make-dirs

autodelete:
	uv run mgallery.py -a

scan:
	uv run mgallery.py -s

autoclean: setup scan autodelete

dump:
	uv run mgallery.py -d

compare:
	uv run mgallery.py -c

rename:
	uv run mgallery.py -r

resort:
	uv run mgallery.py -o

thumbnails:
	uv run mgallery.py -t

check:
	git add .
	uv run pre-commit run

pip:
	uv sync --all-extras --dev

update:
	uv run uv-bump
	uv sync --all-extras --dev
	uv run pre-commit autoupdate
