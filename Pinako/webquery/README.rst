========
WebQuery
========

*This is a crude imitation of YQL using Python and SQLite.*

Dependencies:
 - yaml
 - lxml
 - apsw

Interactive shell:
 `./webquery.py *.yml`

Using a pipe:
 `echo "SELECT * FROM delicious_feeds_popular WHERE query='test' ORDER BY url DESC; SELECT url,title FROM microsoft_bing_web WHERE query='test' LIMIT 5;" | ./webquery.py *.yml`

Limiting requests: (useful for sorting)
 `echo "UPDATE __webquery_v__ SET value=50 WHERE name='microsoft_bing_web_truncate'; SELECT title,url FROM microsoft_bing_web WHERE query='sushi' ORDER BY title;" | ./webquery.py *.yml`

nb:
 - The ORDER BY clause does not map to server-side sorting; it sorts the results that are returned by the server.
 - Request truncation (by the `truncate` variable) always takes precedence over the LIMIT clause, preventing unbounded requests while performing a sorted query. It does not guarantee that the result set be smaller than the set value, so the LIMIT clause is still useful.
