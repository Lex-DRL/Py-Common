"""
Enum-style module specifying the modes supported by encoding detection for txt-file.

No external dependencies:
	*
		**BUILT_IN**: Detect only `ascii` or `utf-8` (with 1.0 precision) if possible,
		use the default system's codepage (with 0.0 precision) otherwise.

Depending on external modules,
the above "dummy" check (BOM/UTF-8/ASCII) is **NOT** performed:
	* **CHARDET**: use `chardet` module only.
	* **CHARDET_DAMMIT**: use `chardet` **WITH** `beautifulsoup4.UnicodeDammit`.

A combination of both previous approaches.
First, try to detect the encoding the "dummy" way (BOM/UTF-8/ASCII).
Then, if no success, use the modules specified above:
	* **FALLBACK_CHARDET**
	* **FALLBACK_CHARDET_DAMMIT**

"""

BUILT_IN = 0

CHARDET = 1
CHARDET_DAMMIT = 2

FALLBACK_CHARDET = 3
FALLBACK_CHARDET_DAMMIT = 4
