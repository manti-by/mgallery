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
	python mgallery.py -a

dump:
	python mgallery.py -d

scan:
	python mgallery.py -s

compare:
	python mgallery.py -c

rename:
	python mgallery.py -r

resort:
	python mgallery.py -o

thumbnails:
	python mgallery.py -t

check:
	git add .
	pre-commit run

pip:
	uv pip install -r requirements.txt

update:
	pcu requirements.txt -u
	pre-commit autoupdate
