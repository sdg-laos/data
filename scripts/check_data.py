from sdg.open_sdg import open_sdg_check
from alter_data import alter_data
from alter_meta import alter_meta

# Validate the indicators.
validation_successful = open_sdg_check(config='config_data.yml',
                                       alter_data=alter_data,
                                       alter_meta=alter_meta)

if not validation_successful:
    raise Exception('There were validation errors. See output above.')
