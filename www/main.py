#!/usr/bin/env python3
# coding: utf-8
import datetime
import http.client
import logging
import os.path
import sys

import flask
from flask.ext import babel
import werkzeug

from config import config
import bib_parser
import search
import index
import messenger
import utils
import utils_flask

if (not os.path.exists("templates")):
	logging.error("Should run from root folder")
	sys.exit(1)

items = bib_parser.BibParser().parse_folder(os.path.abspath("../bib"))
item_index = index.Index(items)
for item in items:
	item.process_crossrefs(item_index)
item_index.update(items)

langid = sorted(item_index["langid"].keys())
keywords = set(item_index["keywords"].keys())

flask_app = flask.Flask(__name__)
flask_app.config["BABEL_DEFAULT_LOCALE"] = config.www.languages[0]
flask_app.config["USE_EVALEX"] = False
babel_app = babel.Babel(flask_app)

flask_app.jinja_env.trim_blocks = True
flask_app.jinja_env.bytecode_cache = utils_flask.MemoryCache()

EXPIRES = datetime.datetime.today() + datetime.timedelta(days=1000)

@flask_app.before_first_request
def initialize():
	logging.info("Starting up")

@babel_app.localeselector
def get_locale():
	"""
	Extracts locale from request
	"""
	lang = flask.request.cookies.get("lang", None)
	if (lang in config.www.languages):
		return lang
	else:	
		return flask.request.accept_languages.best_match(config.www.languages)


@flask_app.route(config.www.app_prefix + "/secret-cookie")
def secret_cookie():
	response = flask.make_response(flask.redirect(config.www.app_prefix + "/index.html"))
	response.set_cookie(
		config.www.secret_cookie_key, 
		value=config.www.secret_cookie_value, 
		expires=EXPIRES
	)
	return response


@flask_app.route(config.www.app_prefix)
def redirect_root():
	desired_language = flask.request.values.get("lang", None)
	next_url = config.www.app_prefix + "/index.html"

	#if lang param is set, redirecting user back to the page he came from
	if (desired_language is not None) and \
		(desired_language in config.www.languages):
		referrer = flask.request.referrer
		if referrer is not None:
			next_url = referrer
		response = flask.make_response(flask.redirect(next_url))
		response.set_cookie("lang", value=desired_language, expires=EXPIRES)
		return response
	else:	
		return flask.redirect(next_url)


@flask_app.route(config.www.app_prefix + "/index.html")
@utils_flask.check_secret_cookie()
def root(show_secrets):
	args_filter = lambda pair: len(pair[1]) > 0
	request_args = dict(filter(args_filter, flask.request.args.items()))
	request_keys = set(request_args.keys())

	#if request_args is empty, we should render empty search form
	if len(request_args) == 0:
		return flask.render_template(
			"index.html", 
			items=items,
			show_secrets=show_secrets
		)

	found_items = None

	for index_to_use in (config.www.indexed_search_params & request_keys):
		value_to_use = request_args[index_to_use]

		if index_to_use in config.parser.list_params:
			values_to_use = utils.strip_split_list(value_to_use, ",")
		else:
			values_to_use = [value_to_use]

		for value in values_to_use:
			indexed_items = set(item_index[index_to_use].get(value, set()))
			if found_items is None:
				found_items = indexed_items
			else:
				found_items &= indexed_items
	
	searches = []
	if found_items is None:
		#no index was applied
		found_items = items
	
	try:
		for search_key in (config.www.nonindexed_search_params & request_keys):
			# argument can be missing or be empty
			# both cases should be ignored during search
			search_param = request_args[search_key]
			if len(search_param) > 0:
				param_filter = search.search_for(search_key, search_param)
				if param_filter is not None:
					searches.append(param_filter)
	except Exception as ex:
		flask.abort(400, "Some of the search parameters are wrong: {0}".format(ex))

	if len(searches) > 0:
		found_items = list(filter(search.and_(searches), found_items))

	return flask.render_template(
		"index.html", 
		found_items=found_items,
		search_params=request_args,
		show_secrets=show_secrets
	)


@flask_app.route(config.www.app_prefix + "/all.html")
@utils_flask.check_secret_cookie()
def show_all(show_secrets):
	return flask.render_template(
		"all.html", 
		items=items,
		show_secrets=show_secrets
	)


@flask_app.route(config.www.app_prefix + "/book/<string:id>", methods=["GET"])
@utils_flask.check_secret_cookie()
def get_book(id, show_secrets):
	
	items = item_index["id"].get(id, None)
	
	if items is None:
		flask.abort(404, "Book with id {id} was not found".format(id=id))
	elif len(items) != 1:
		flask.abort(500, "Multiple entries with id {id}".format(id=id))
	item = next(iter(items))
	return flask.render_template(
		"book.html", 
		item=item,
		show_secrets=show_secrets
	)


@flask_app.route(config.www.app_prefix + "/book/<string:book_id>", methods=["POST"])
@utils_flask.jsonify()
def edit_book(book_id):
	items = item_index["id"].get(book_id, None)

	if items is None:
		flask.abort(404, "Book with id {id} was not found".format(id=id))
	elif len(items) != 1:
		flask.abort(500, "Multiple entries with id {id}".format(id=id))
	
	message = utils_flask.extract_string_from_request("message")
	from_name = utils_flask.extract_string_from_request("name")
	from_email = utils_flask.extract_email_from_request("email")
	if not all([message, from_name, from_email]):
		flask.abort(400, "Empty values aren't allowed")
	
	message = messenger.Message(book_id, from_email, from_name, message)
	message.send()

	return {"result": "OK", "message": babel.gettext("thanks")}


@flask_app.route(config.www.app_prefix + "/langid", methods=["GET"])
@utils_flask.jsonify()
def get_languages():
	return dict(zip(langid, map(babel.gettext, langid)))


@flask_app.route(config.www.app_prefix + "/keywords", methods=["GET"])
@utils_flask.check_secret_cookie()
@utils_flask.jsonify()
def get_keywords(show_secrets):
	data = keywords
	if not show_secrets:
		data -= config.www.secret_keywords
	return sorted(data)


@flask_app.route(config.www.app_prefix + "/<path:filename>", methods=["GET"])
def everything_else(filename):
	if (os.path.isfile("templates/" + filename)):
		return flask.render_template(filename)
	elif (os.path.isfile("static/" + filename)):
		return flask_app.send_static_file(filename)
	else:
		flask.abort(404, "No such file")


if __name__ == "__main__":
	flask_app.run(host="0.0.0.0")
else:
	for code in werkzeug.HTTP_STATUS_CODES:
		#registering only required code
		if http.client.BAD_REQUEST <= code:
			flask_app.errorhandler(code)(utils_flask.xml_exception_handler)
	flask_app.errorhandler(Exception)(utils_flask.xml_exception_handler)

