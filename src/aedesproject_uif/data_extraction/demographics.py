#!/usr/bin/env python
# coding: utf-8

"""
Demographic data extraction module.

This module provides functions to fetch demographic data including relative wealth
index and population density from the Humanitarian Data Exchange (HDX) platform.
"""

import logging
import os
import re
from pathlib import Path
from typing import Optional

import requests

# Set up logging
logger = logging.getLogger(__name__)


class DemographicsDataError(Exception):
    """Custom exception for demographic data extraction errors."""
    pass


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


def _validate_segment(segment: str) -> None:
    """
    Validate population density segment.

    Args:
        segment: Segment type (e.g., 'general')

    Raises:
        ValueError: If segment is invalid
    """
    valid_segments = ["general", "children", "women", "youth"]
    if segment.lower() not in valid_segments:
        raise ValueError(
            f"Invalid segment: {segment}. "
            f"Choose from: {', '.join(valid_segments)}"
        )


def fetch_relative_wealth_index(
    country: str,
    iso_country_code: str,
    timeout: int = 30
) -> None:
    """
    Fetch relative wealth index data from HDX.

    This function retrieves the relative wealth index CSV file for a given country
    from the Humanitarian Data Exchange platform.

    Args:
        country: Country name (e.g., 'Philippines')
        iso_country_code: ISO 3166-1 alpha-3 country code (e.g., 'PHL')
        timeout: Request timeout in seconds (default: 30)

    Raises:
        DemographicsDataError: If data cannot be fetched or saved
        ValueError: If country code is invalid

    Returns:
        None

    Example:
        >>> fetch_relative_wealth_index('Philippines', 'PHL')
    """
    _validate_country_code(iso_country_code)

    url = "https://data.humdata.org/dataset/relative-wealth-index"

    try:
        logger.info(f"Fetching relative wealth index for {country} ({iso_country_code})")
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

    except requests.RequestException as e:
        error_msg = f"Failed to access {url}: {str(e)}"
        logger.error(error_msg)
        raise DemographicsDataError(error_msg) from e

    # Use regular expression to find the download URL
    pattern = re.compile(
        rf"https://data\.humdata\.org/dataset/[\w\d-]+/resource/[\w\d-]+/"
        rf"download/{iso_country_code.lower()}_relative_wealth_index\.csv"
    )
    match = pattern.search(response.text)

    if not match:
        error_msg = f"No relative wealth index data found for {country}"
        logger.warning(error_msg)
        raise DemographicsDataError(error_msg)

    download_url = match.group(0)
    download_rwi(download_url, country, iso_country_code, timeout)


def download_rwi(
    url: str,
    country: str,
    iso_country_code: str,
    timeout: int = 30
) -> Path:
    """
    Download relative wealth index CSV file.

    Args:
        url: Direct download URL for the CSV file
        country: Country name
        iso_country_code: ISO 3166-1 alpha-3 country code
        timeout: Request timeout in seconds (default: 30)

    Returns:
        Path to the downloaded file

    Raises:
        DemographicsDataError: If download fails

    Example:
        >>> path = download_rwi('https://...', 'Philippines', 'PHL')
        >>> print(path)
    """
    _validate_country_code(iso_country_code)

    try:
        logger.info(f"Downloading relative wealth index for {country}")
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

    except requests.RequestException as e:
        error_msg = f"Failed to download file from {url}: {str(e)}"
        logger.error(error_msg)
        raise DemographicsDataError(error_msg) from e

    # Create output directory
    file_dir = Path.home().parent / "data" / "Demographic" / iso_country_code
    file_dir.mkdir(parents=True, exist_ok=True)

    file_path = file_dir / f"{iso_country_code}_relative_wealth_index.csv"

    try:
        with open(file_path, "wb") as f:
            f.write(response.content)
        logger.info(f"File downloaded successfully: {file_path}")
        return file_path

    except IOError as e:
        error_msg = f"Failed to write file to {file_path}: {str(e)}"
        logger.error(error_msg)
        raise DemographicsDataError(error_msg) from e


def fetch_population_density(
    country: str,
    iso_country_code: str,
    segment: str = "general",
    timeout: int = 30
) -> None:
    """
    Fetch population density data from HDX.

    This function retrieves the population density GeoTIFF file for a given country
    and population segment from the Humanitarian Data Exchange platform.

    Args:
        country: Country name (e.g., 'Philippines')
        iso_country_code: ISO 3166-1 alpha-3 country code (e.g., 'PHL')
        segment: Population segment ('general', 'children', 'women', 'youth')
        timeout: Request timeout in seconds (default: 30)

    Raises:
        DemographicsDataError: If data cannot be fetched or saved
        ValueError: If country code or segment is invalid

    Returns:
        None

    Example:
        >>> fetch_population_density('Philippines', 'PHL', 'general')
    """
    _validate_country_code(iso_country_code)
    _validate_segment(segment)

    url = "https://data.humdata.org/dataset/philippines-high-resolution-population-density-maps-demographic-estimates"

    try:
        logger.info(f"Fetching {segment} population density for {country} ({iso_country_code})")
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

    except requests.RequestException as e:
        error_msg = f"Failed to access {url}: {str(e)}"
        logger.error(error_msg)
        raise DemographicsDataError(error_msg) from e

    # Use regular expression to find the download URL
    pattern = re.compile(
        rf"https://.*?download/{iso_country_code.lower()}_{segment}.*_geotiff\.zip"
    )
    match = pattern.search(response.text)

    if not match:
        error_msg = f"No {segment} population density data found for {country}"
        logger.warning(error_msg)
        raise DemographicsDataError(error_msg)

    download_url = match.group(0)
    logger.info(f"Beginning download for {country} segment {segment}. This may take a while due to file size.")
    download_popmap(download_url, country, iso_country_code, segment, timeout)


def download_popmap(
    url: str,
    country: str,
    iso_country_code: str,
    segment: str = "general",
    timeout: int = 30
) -> Path:
    """
    Download population density GeoTIFF file.

    Args:
        url: Direct download URL for the ZIP file
        country: Country name
        iso_country_code: ISO 3166-1 alpha-3 country code
        segment: Population segment (e.g., 'general')
        timeout: Request timeout in seconds (default: 30)

    Returns:
        Path to the downloaded file

    Raises:
        DemographicsDataError: If download fails

    Example:
        >>> path = download_popmap('https://...', 'Philippines', 'PHL', 'general')
        >>> print(path)
    """
    _validate_country_code(iso_country_code)
    _validate_segment(segment)

    try:
        logger.info(f"Downloading {segment} population density data for {country}")
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()

    except requests.RequestException as e:
        error_msg = f"Failed to download file from {url}: {str(e)}"
        logger.error(error_msg)
        raise DemographicsDataError(error_msg) from e

    # Create output directory
    file_dir = Path.home().parent / "data" / "Demographic" / iso_country_code
    file_dir.mkdir(parents=True, exist_ok=True)

    file_path = file_dir / f"{iso_country_code}_{segment}_population_density.zip"

    try:
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logger.info(f"File downloaded successfully: {file_path}")
        return file_path

    except IOError as e:
        error_msg = f"Failed to write file to {file_path}: {str(e)}"
        logger.error(error_msg)
        raise DemographicsDataError(error_msg) from e


if __name__ == "__main__":
    # Example usage (uncomment to run)
    # fetch_population_density("Philippines", "PHL", "general")
    # fetch_relative_wealth_index("Philippines", "PHL")
    pass

