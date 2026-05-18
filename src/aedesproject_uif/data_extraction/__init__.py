# Submodules use optional heavy dependencies (fiona, geopandas, pytrends, osmnx, wget).
# Import each submodule directly rather than via wildcard to avoid loading unused deps.
# e.g.: from aedesproject_uif.data_extraction.demographics import fetch_relative_wealth_index
