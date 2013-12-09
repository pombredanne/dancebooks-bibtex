#!/usr/bin/env python
# coding: utf-8
import os.path

import constants
import main
import parser
import utils

client = main.app.test_client()

@utils.profile()
def all_profile():
	client.get(constants.APP_PREFIX + "/all.html")
	

@utils.profile
def parsing_profile():
	bib_parser = parser.BibParser()
	bib_parser.parse_folder(os.path.abspath("../bib"))


@utils.profile
def search_profile():
	client.get("/bib/index.html?"
		"title=Dance&"
		"author=Wil&"
		"year_from=1000&"
		"year_to=2000")


if __name__ == "__main__":
	all_profile()
	#parsing_profile()
	#search_profile()
	pass
