#!/usr/bin/env python3
"""
Search orchestrator that generates all queries needed for digest generation.
"""
import sys
import json
sys.path.insert(0, 'src')

from date_utils import get_last_week_range
from news_collector import NewsCollector
import config

def main():
    """Generate all search queries."""
    start_date, end_date = get_last_week_range()
    collector = NewsCollector(start_date, end_date)

    all_queries = {}
    for jur_code in config.ALL_JURISDICTIONS.keys():
        queries = collector.build_search_queries(jur_code)
        all_queries[jur_code] = queries

    # Print queries as JSON
    print(json.dumps(all_queries, indent=2))

if __name__ == '__main__':
    main()
