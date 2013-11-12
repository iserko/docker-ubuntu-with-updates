
TODAY := $(shell date +"%Y%m%d")

env:
	./bin/bootstrap-virtualenv.sh

clean:
	find . -name '*.pyc' -delete
	rm -rf dist build *.egg-info

clean_docker: clean
	./bin/builder.py cleanup_containers
	./bin/builder.py cleanup_images

precise: clean_docker
	./bin/builder.py precise ${TODAY}
	./bin/builder.py flatten precise-with-updates:${TODAY}
	sleep 10
	./bin/builder.py retag precise-with-updates:${TODAY} racker/precise-with-updates:${TODAY}
	./bin/builder.py retag precise-with-updates:${TODAY} racker/precise-with-updates:latest

precise-upload: precise
	./bin/builder.py push racker/precise-with-updates

.PHONY: precise clean clean_docker env precise-upload
