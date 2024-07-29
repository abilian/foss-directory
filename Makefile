.PHONY: run install test clean clear format boot

all: test check

## Run tests
test:
	-dropdb test
	createdb test
	pytest

## Run static check
check:
	ruff src
	# flake8 src

## Run dev server
run:
	FLASK_DEBUG=true flask dev
	# honcho start

## Build static assets
build:
	flask tailwind build

## Deploy to production
deploy: clean
	fab -e deploy

## Clean up
clean:
	adt clean
	find . -name __pycache__ -print0 | xargs -0 rm -rf
	find . -name .DS_Store -print0 | xargs -0 rm -rf

## Super clean up
tidy: clean
	rm -rf .pytest_cache .tox .nox


#install:
#	pip install -U pip setuptools wheel
#	pip install -r requirements.txt
#
#run:
#	flask devserver
#
#start-server:
#	gunicorn -D -w1 --timeout 300 \
#		--bind unix:run/gunicorn.sock \
#		--pid run/gunicorn.pid \
#		--capture-output \
#		--access-logfile run/access.log \
#		--error-logfile run/error.log \
#		wsgi:app
#
#stop-server:
#	kill `cat run/gunicorn.pid`
#
#restart-server:
#	kill -HUP `cat run/gunicorn.pid`
#
#
#clear:
#	rm -rf var/*
#
#format:
#	black *.py app scripts
#	isort -rc *.py app scripts
#	cd front && make format
#
#deploy: clean
#	# @make build
#	@make push
#	python scripts/deploy.py
#	#ssh pilaf "cd annuaire-cnll && ./env/bin/pip install -q -r requirements.txt"
#	ssh pilaf "cd annuaire-cnll && make restart-server"
#
#push:
#	rsync --exclude env --exclude .env --exclude data \
#		--exclude .git --exclude .idea \
#		--exclude front/node_modules \
#		--exclude nuxt/node_modules \
#		--exclude run \
#		--delete-after -e ssh -avz . pilaf:annuaire-cnll/
#
#
#boot:
#	flask clear-data
#	flask load-data
#	flask import-descriptions
#	flask geocode
#	flask take-screenshots
#


## Format source code
format:
	black *.py src tests scripts migrations
	isort *.py src tests scripts

## Prepare data
boot:
	flask clear-data
	flask load-data
	flask import-descriptions
	flask geocode
	flask take-screenshots

## Update dependencies
update-deps:
	pip install -U pip wheel setuptools
	poetry update
	# dephell deps convert --from=pyproject.toml --to=requirements.txt --envs main
	# dephell deps convert --from=pyproject.toml --to=setup.py
	black setup.py

## Push to prod
push: clean
	rsync -e ssh -avz ./ pilaf:annuaire-cnll/backend/


help:
	adt help-make
