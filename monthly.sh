#!/bin/sh

set -e

flask sirene import-unites-legales
flask sirene import-etablissements

flask crawler reset-session
flask crawler seed
flask crawler crawl

