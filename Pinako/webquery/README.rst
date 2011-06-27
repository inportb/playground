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

nb:
 - Unless you know what you're doing, you should always LIMIT your queries. SELECTing from Bing without LIMIT would result in *lots* of requests.
 - Server-side sorting is not supported yet. If you use a client-side ORDER BY, you'd end up retrieving much more than you need to. For now, use a TEMPORARY TABLE if you need to sort the results.
