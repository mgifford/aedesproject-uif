#!/usr/bin/env python
# coding: utf-8

"""
Google Trends data extraction module.

This module provides functions to fetch and process Google Trends data
for dengue-related searches across geographic regions.
"""

import logging
import os
import random
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd
from pytrends.request import TrendReq

# Set up logging
logger = logging.getLogger(__name__)


class GoogleTrendsError(Exception):
    """Custom exception for Google Trends data extraction errors."""
    pass


def _validate_date_format(date_str: str) -> None:
    """
    Validate date string format (YYYY-MM-DD).

    Args:
        date_str: Date string to validate

    Raises:
        ValueError: If date format is invalid
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(
            f"Invalid date format: {date_str}. Expected YYYY-MM-DD"
        )


def _validate_country_code(iso_country_code: str) -> None:
    """
    Validate ISO country code format.

    Args:
        iso_country_code: ISO 3166-1 alpha-3 country code

    Raises:
        ValueError: If country code is invalid
    """
    if not iso_country_code or len(iso_country_code) != 3 or not iso_country_code.isalpha():
        raise ValueError(
            f"Invalid country code: {iso_country_code}. "
            "Expected 3-letter ISO 3166-1 alpha-3 code."
        )


def _load_subdivision_data(iso_country_code: str) -> pd.DataFrame:
    """
    Load subdivision data for a country.

    Args:
        iso_country_code: ISO 3166-1 alpha-3 country code

    Returns:
        DataFrame containing subdivision information

    Raises:
        GoogleTrendsError: If subdivision data cannot be loaded
    """
    csv_file_path = Path.home().parent / "data" / f"Subdivision_{iso_country_code}.csv"

    if not csv_file_path.exists():
        error_msg = f"Subdivision data not found: {csv_file_path}"
        logger.error(error_msg)
        raise GoogleTrendsError(error_msg)

    try:
        return pd.read_csv(csv_file_path)
    except pd.errors.ParserError as e:
        error_msg = f"Failed to parse subdivision data: {str(e)}"
        logger.error(error_msg)
        raise GoogleTrendsError(error_msg) from e


def _get_related_keywords(
    pytrends: TrendReq,
    keyword: str,
    timeframe: str,
    geo: str
) -> List[str]:
    """
    Get related keywords for a given search term.

    Args:
        pytrends: TrendReq instance
        keyword: Primary search keyword
        timeframe: Time period for search
        geo: Geographic location code

    Returns:
        List of related keywords

    Raises:
        GoogleTrendsError: If related queries cannot be retrieved
    """
    try:
        pytrends.build_payload(
            [keyword],
            timeframe=timeframe,
            geo=geo,
            gprop=""
        )
        rel_queries = pytrends.related_queries()

        if rel_queries and keyword in rel_queries:
            dengue_data = rel_queries[keyword]
            rising_queries = dengue_data.get("rising")
            top_queries = dengue_data.get("top")

            rising_list = (
                rising_queries["query"].tolist()
                if rising_queries is not None else []
            )
            top_list = (
                top_queries["query"].tolist()
                if top_queries is not None else []
            )

            kw_list = [keyword] + rising_list + top_list
            return list(set(kw_list))
        else:
            return [keyword]

    except Exception as e:
        logger.warning(f"Failed to get related keywords for {keyword}: {str(e)}")
        return [keyword]


def fetch_google_trends(
    iso_country_code: str,
    start_date: str,
    end_date: str,
    keywords: Optional[List[str]] = None,
    sleep_interval: tuple = (10, 20),
    timeout: int = 30
) -> pd.DataFrame:
    """
    Fetch Google Trends data for dengue-related searches.

    This function retrieves Google Trends data for specified keywords across
    geographic subdivisions within a country for a given time period.

    Args:
        iso_country_code: ISO 3166-1 alpha-3 country code (e.g., 'PHL')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        keywords: List of keywords to search (default: ['dengue'])
        sleep_interval: Tuple of (min, max) seconds to sleep between requests
        timeout: Request timeout in seconds (default: 30)

    Returns:
        DataFrame containing Google Trends data

    Raises:
        GoogleTrendsError: If data cannot be fetched
        ValueError: If dates or country code are invalid

    Example:
        >>> df = fetch_google_trends('PHL', '2016-01-10', '2021-01-10')
        >>> print(df.head())
    """
    # Validate inputs
    _validate_country_code(iso_country_code)
    _validate_date_format(start_date)
    _validate_date_format(end_date)

    if keywords is None:
        keywords = ["dengue"]

    # Load subdivision data
    iso_df = _load_subdivision_data(iso_country_code)

    # Initialize PyTrends
    pytrends = TrendReq(
        hl='en-US',
        tz=360,
        timeout=timeout,
        retries=3,
        backoff_factor=0.5
    )

    # Initialize DataFrame to store results
    df_trends = pd.DataFrame()
    timeframe = f'{start_date} {end_date}'

    logger.info(
        f"Starting Google Trends fetch for {iso_country_code} "
        f"from {start_date} to {end_date}"
    )

    for index, row in iso_df.iterrows():
        geo = row['ISO 3166-2']
        region = row['Region']

        try:
            # Get related keywords
            kw_list = _get_related_keywords(pytrends, keywords[0], timeframe, geo)

            # Fetch trends for each keyword
            for kw in kw_list:
                try:
                    pytrends.build_payload(
                        kw_list=[kw],
                        timeframe=timeframe,
                        geo=geo,
                        gprop=''
                    )
                    search_vol = pytrends.interest_over_time().reset_index()
                    search_vol = search_vol.rename(columns={kw: "value"})
                    search_vol["keyword"] = kw
                    search_vol["geo"] = geo
                    search_vol["region"] = region
                    search_vol["date_extracted"] = pd.Timestamp.now().strftime('%Y-%m-%d')

                    df_trends = pd.concat([df_trends, search_vol], ignore_index=True)

                except Exception as e:
                    logger.warning(f"Error fetching trends for keyword '{kw}' in {geo}: {e}")
                    continue

            logger.info(f"Successfully scraped trends for: {geo}")

        except Exception as e:
            logger.error(f"Error occurred for geo {geo}: {e}")
            time.sleep(60)  # Sleep for 60 seconds before retrying
            continue

        # Random sleep to avoid rate limiting
        sleep_time = random.randint(sleep_interval[0], sleep_interval[1])
        time.sleep(sleep_time)

    if df_trends.empty:
        error_msg = "No Google Trends data was retrieved"
        logger.error(error_msg)
        raise GoogleTrendsError(error_msg)

    logger.info(f"Google Trends fetch completed. Retrieved {len(df_trends)} records")
    return df_trends


def save_google_trends(
    df: pd.DataFrame,
    iso_country_code: str,
    output_dir: Optional[Path] = None
) -> Path:
    """
    Save Google Trends data to CSV file.

    Args:
        df: DataFrame containing trends data
        iso_country_code: ISO 3166-1 alpha-3 country code
        output_dir: Output directory (default: data/Google Trends)

    Returns:
        Path to the saved file

    Raises:
        IOError: If file cannot be written
    """
    if output_dir is None:
        output_dir = Path.home().parent / "data" / "Google Trends"

    output_dir.mkdir(parents=True, exist_ok=True)
    save_path = output_dir / f"{iso_country_code}.csv"

    try:
        df.to_csv(save_path, index=False)
        logger.info(f"Google Trends data saved to {save_path}")
        return save_path
    except IOError as e:
        error_msg = f"Failed to save Google Trends data: {str(e)}"
        logger.error(error_msg)
        raise IOError(error_msg) from e


if __name__ == "__main__":
    # Example usage (uncomment to run)
    # df = fetch_google_trends('PHL', '2016-01-10', '2021-01-10')
    # save_google_trends(df, 'PHL')
    pass




