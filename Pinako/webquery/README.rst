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
