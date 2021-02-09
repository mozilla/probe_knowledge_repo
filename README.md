# Probe Resource Files (Prototype)

This is intended to be a proof of concept repository meant to house knowledge and resources about our telemetry probes.

Each probe for Firefox Desktop and Fenix has its own yaml file found in the `./metrics/fenix` and `./metrics/firefox_desktop` directories.

Files are split into two sections - the first section contains basic information reproduced from the probe dictionaries. The second section contains user-editable fields meant to be easily updated with links, tribal knowledge, gotchas etc about how the probe can be used analyzed. These yaml files can be edited directly in github.

`functions.py` contains some (pretty hacky) python functions for pulling probe data down from the [probe info service](https://mozilla.github.io/probe-scraper/) and writing/updating the probe yaml files. Specifically:

* `update_file_list` will pull down the most recent probe data from the probe info service and update existing yaml files where needed, as well as write new files if it finds new probes. This function will NOT overwrite what's been added to the user-editable sections of the existing yaml files.

* `build_files` will create the per-probe yaml files from scratch. This function WILL overwrite any previous changes to the user-editable sections.

```bash
python3 -m venv venv
pip install -r requirements.txt
```
