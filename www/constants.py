#options actual for parsing

#parameters containing lists
LIST_PARAMS = frozenset(["location", "isbn", "origlanguage"])
LISTSEP = "|"

#parameters containing names
NAMESEP = "|"
NAME_PARAMS = frozenset(["author", "publisher", "translator"])

#parameters containing keywords
KEYWORDSEP = ","
KEYWORD_PARAMS = frozenset(["keywords"])

#union of all the above
MULTI_VALUE_PARAMS = LIST_PARAMS | NAME_PARAMS | KEYWORD_PARAMS

#parameters to be scanned (returned as a union)
SCAN_FIELDS = set(["langid", "keywords"])

#options actual for searching

#available search keys
AVAILABLE_SEARCH_KEYS = [
	"author", "title", "langid", "publisher", "location", "keywords"
	]

#parameters for year searching
YEAR_PARAM = "year"
YEAR_TO_PARAM = "year_to"
YEAR_FROM_PARAM = "year_from"

#options actual for output
#output list separator
OUTPUT_LISTSEP = ", "

