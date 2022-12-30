# Cached Chrome Top Million Websites

[Recent research](https://zakird.com/papers/toplists.pdf) showed that the top
million most popular websites published by Google Chrome via the [Chrome UX
Report](https://developer.chrome.com/docs/crux/) is _significantly_ more
accurate than other top lists like the Alexa Top Million and Tranco Top
Million.

This repository caches a CSV version of the Chrome top sites, queried from the
CrUX data in Google BigQuery. You can browse all of the cached lists
[here](https://github.com/zakird/crux-top-lists/tree/main/data/global). The
most up-to-date top million global websites can be downloaded directly at:
https://raw.githubusercontent.com/zakird/crux-top-lists/main/data/global/current.csv.gz.

### Data Structure

The CrUX dataset has several important differences from other top lists:

1. Websites are bucketed by rank magnitude order, not by specific rank.
   Rank will be 1000, 10K, 100K, or 1M in the provided files. The data is
   ordered by rank magnitude. Within each order of magnitude, websites are
   listed randomly.

2. Websites are identified by _origin_ (e.g., https://www.google.com) not
   by domain or FQDN.

3. Data is released monthly, typically on the second Tuesday of the month.

For example, this is what data looks like:

```
origin,rank
https://www.ptwxz.com,1000
https://ameblo.jp,1000
https://danbooru.donmai.us,1000
https://game8.jp,1000
https://www.google.com.au,1000
https://www.repubblica.it,1000
https://www.w3schools.com,1000
https://animekimi.com,1000
```

### Why 1 Million Sites?

This repository does not contain all of the website ranking data published by
Chrome. Their global list of popular websites contains approximately 15M
websites (~650MB download). The top million websites captures over 95% of user
traffic in Chrome by both Page Loads and Time on Page ([Ruth et
al.](https://zakird.com/papers/browsing.pdf)) and is a reasonable
approximation:

<p align="center">
<img width="500" alt="CDF of User Traffic" src="https://user-images.githubusercontent.com/201296/210084850-a31e3d5d-7108-48aa-8271-c05a7ee10a23.png">
</p>

The following SQL can be used to generate similarly a similar list of all
globally popular websites:

```sql
SELECT distinct origin, experimental.popularity.rank
    FROM `chrome-ux-report.experimental.global`
    WHERE yyyymm = ? -- e.g., integer 202210
    GROUP BY origin, experimental.popularity.rank
    ORDER BY experimental.popularity.rank;
```

### Country-Specific Websites

In addition, Chrome publishes country-specific top lists in BigQuery.

The following SQL can be used to dump out country-specific top websites:

```sql
SELECT distinct country_code, origin, experimental.popularity.rank
    FROM `chrome-ux-report.experimental.country`
    WHERE yyyymm = ? -- e.g., integer 202210
		AND experimental.popularity.rank <= 1000000
    GROUP BY country_code, origin, experimental.popularity.rank
    ORDER BY country_code, experimental.popularity.rank;
```
