#!/usr/bin/env python
# coding: utf-8

"""
OpenStreetMap (OSM) data extraction module.

This module provides functions to fetch and process OpenStreetMap features
such as buildings, amenities, shops, and water bodies.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import geopandas as gpd
import osmnx as ox
import pandas as pd
from retrying import retry

# Set up logging
logger = logging.getLogger(__name__)

# Configure OSM settings
ox.settings.timeout = 60


class OSMDataError(Exception):
    """Custom exception for OSM data extraction errors."""
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


def _validate_admin_level(admin_level: int) -> None:
    """
    Validate administrative level.

    Args:
        admin_level: Administrative boundary level

    Raises:
        ValueError: If admin level is invalid
    """
    if not isinstance(admin_level, int) or admin_level < 0 or admin_level > 10:
        raise ValueError(
            f"Invalid admin_level: {admin_level}. "
            "Expected integer between 0 and 10."
        )


def retry_if_file_not_found_error(exception: Exception) -> bool:
    """Retry decorator condition for FileNotFoundError."""
    return isinstance(exception, FileNotFoundError)


def create_directory(path: str) -> None:
    """
    Create a directory if it doesn't exist.

    Args:
        path: Directory path to create
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        logger.info(f"Created directory: {path}")


@retry(
    retry_on_exception=retry_if_file_not_found_error,
    stop_max_attempt_number=3,
    wait_fixed=2000
)
def fetch_osm(
    iso_country_code: str,
    admin_level: int,
    tags: Optional[Dict[str, bool]] = None,
    output_dir: Optional[Path] = None
) -> Dict[str, Path]:
    """
    Fetch OpenStreetMap features from a GeoJSON file and save as CSV.

    This function reads GeoJSON administrative boundary files, queries
    OpenStreetMap for specified features, and saves the results as CSV files.

    Args:
        iso_country_code: ISO 3166-1 alpha-3 country code (e.g., 'PHL')
        admin_level: Administrative boundary level (0-10)
        tags: Dictionary of OSM tags to query (e.g., {'building': True})
        output_dir: Output directory path (default: data/OpenStreetMap)

    Returns:
        Dictionary mapping tag names to output file paths

    Raises:
        OSMDataError: If data cannot be fetched or processed
        ValueError: If country code or admin level is invalid

    Example:
        >>> paths = fetch_osm('PHL', 2)
        >>> print(paths)
    """
    # Validate inputs
    _validate_country_code(iso_country_code)
    _validate_admin_level(admin_level)

    if tags is None:
        tags = {
            "building": True,
            "amenity": True,
            "shop": True,
            "water": True
        }

    if output_dir is None:
        output_dir = Path.home().parent / "data" / "OpenStreetMap" / iso_country_code / f"ADM{admin_level}"
    else:
        output_dir = Path(output_dir)

    # Set up paths
    src_path = Path.home().parent / "data" / "GeoJSON" / iso_country_code / f"ADM{admin_level}"

    if not src_path.exists():
        error_msg = f"Source GeoJSON directory not found: {src_path}"
        logger.error(error_msg)
        raise OSMDataError(error_msg)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Get list of GeoJSON files
    try:
        admin_list = [
            f.split('.geojson')[0]
            for f in os.listdir(src_path)
            if f.endswith('.geojson')
        ]
    except OSError as e:
        error_msg = f"Failed to list GeoJSON files: {str(e)}"
        logger.error(error_msg)
        raise OSMDataError(error_msg) from e

    if not admin_list:
        error_msg = f"No GeoJSON files found in {src_path}"
        logger.error(error_msg)
        raise OSMDataError(error_msg)

    # Initialize data frames
    tag_dfs: Dict[str, pd.DataFrame] = {tag: pd.DataFrame() for tag in tags.keys()}

    # Load any existing temporary data
    for tag in tag_dfs.keys():
        temp_output_path = output_dir / f"{tag}_temp.csv"
        if temp_output_path.exists():
            try:
                tag_dfs[tag] = pd.read_csv(temp_output_path)
                logger.info(f"Loaded temporary {tag} data from {temp_output_path}")
            except pd.errors.ParserError as e:
                logger.warning(f"Failed to load temporary {tag} data: {e}")

    # Read the last processed location
    last_processed_file = output_dir / "last_processed.txt"
    if last_processed_file.exists():
        try:
            with open(last_processed_file, 'r') as f:
                last_processed = f.read().strip()
            start_index = admin_list.index(last_processed) + 1 if last_processed in admin_list else 0
            logger.info(f"Resuming from location: {admin_list[start_index] if start_index < len(admin_list) else 'end'}")
        except (IOError, ValueError) as e:
            logger.warning(f"Failed to read last processed location: {e}")
            start_index = 0
    else:
        start_index = 0

    logger.info(f"Processing {len(admin_list[start_index:])} administrative boundaries")

    # Process each admin boundary
    for loc in admin_list[start_index:]:
        flnm = src_path / f"{loc}.geojson"

        try:
            gdf = gpd.read_file(flnm)
            logger.info(f"Processing {loc}")

        except FileNotFoundError:
            logger.error(f"File {flnm} not found. Retrying...")
            raise

        except Exception as e:
            logger.error(f"Failed to read GeoJSON file {flnm}: {e}")
            continue

        try:
            geometry = gdf['geometry'].iloc[0]
        except (KeyError, IndexError) as e:
            logger.warning(f"No valid geometry found in {flnm}: {e}")
            continue

        # Extract features for each tag
        for tag in tag_dfs.keys():
            try:
                df = ox.features_from_polygon(geometry, tags={tag: True})

                if not df.empty:
                    cnt_df = pd.DataFrame(df[tag].value_counts()).reset_index().T
                    cnt_df2 = cnt_df.drop(index=[tag])
                    cnt_df2.columns = cnt_df.iloc[0].values.tolist()
                    cnt_df2["Location"] = str(loc)
                    cnt_df2["Date_Extracted"] = datetime.now().strftime('%Y-%m-%d')

                    tag_dfs[tag] = pd.concat([tag_dfs[tag], cnt_df2], ignore_index=True)

            except Exception as e:
                logger.debug(f"No {tag} features found for {loc}: {e}")
                continue

        logger.info(f"Processing for {loc} is complete.")

        # Save intermediate data
        for tag, df in tag_dfs.items():
            temp_output_path = output_dir / f"{tag}_temp.csv"
            try:
                df.to_csv(temp_output_path, index=False)
            except IOError as e:
                logger.error(f"Failed to save temporary {tag} data: {e}")

        # Update the last processed location
        try:
            with open(last_processed_file, 'w') as f:
                f.write(loc)
        except IOError as e:
            logger.error(f"Failed to update last processed location: {e}")

    # Save final data and remove temporary files
    output_files: Dict[str, Path] = {}

    for tag, df in tag_dfs.items():
        output_path = output_dir / f"{tag}.csv"
        try:
            df.to_csv(output_path, index=False)
            output_files[tag] = output_path
            logger.info(f"{tag.capitalize()} data has been saved to {output_path}")

            # Remove temporary file
            temp_output_path = output_dir / f"{tag}_temp.csv"
            if temp_output_path.exists():
                temp_output_path.unlink()

        except IOError as e:
            logger.error(f"Failed to save {tag} data: {e}")

    # Remove the last processed file as all locations have been processed
    if last_processed_file.exists():
        try:
            last_processed_file.unlink()
            logger.info("All locations have been processed successfully.")
        except OSError as e:
            logger.error(f"Failed to remove last_processed.txt: {e}")

    return output_files


if __name__ == "__main__":
    # Example usage (uncomment to run)
    # paths = fetch_osm('PHL', 2)
    # print(paths)
    pass
#    iso_country_code = "PHL"
#    admin_level = 2
#    fetch_osm(iso_country_code, admin_level)

