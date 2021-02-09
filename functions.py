import yaml
import requests
import json
from collections import OrderedDict
from os import listdir, path

FENIX_METRICS_ENDPOINT = "https://probeinfo.telemetry.mozilla.org/glean/fenix/metrics"
FIREFOX_DESKTOP_ENDPOINT ="https://probeinfo.telemetry.mozilla.org/firefox/nightly/main/all_probes"
FENIX_FIELDS = ['type', 'description', 'expires', 'disabled', 'send_in_pings']
FIREFOX_DESKTOP_FIELDS = ['type', 'description', 'expiry_version']
FENIX_FILE_DIRECTORY = "./metrics/fenix/"
FIREFOX_DESKTOP_FILE_DIRECTORY = "./metrics/firefox_desktop/"

def represent_ordereddict(dumper, data):
    """cargo culted from https://stackoverflow.com/questions/16782112/can-pyyaml-dump-dict-items-in-non-alphabetical-order
    allows using an OrderedDict in a yaml dump, so the keys can be sorted in a certain order (i wanted the probe name first)"""
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)

yaml.add_representer(OrderedDict, represent_ordereddict)

def create_one_file(directory, metric, metric_data, fields):
    to_write = OrderedDict()
    if len(metric.split("/")) > 1:
        metric_name = metric.split("/")[1]
    else:
        metric_name = metric
    to_write['name'] = metric_name
    for f in fields:
        if (f == 'type' and len(metric.split("/")) > 1):
            to_write[f] = metric.split("/")[0]
        else:
            to_write[f] = metric_data[f]
    with open(directory + metric_name + '.yaml', 'w') as f:
        _ = yaml.dump(to_write, f)


def add_editable_fields_once(directory, metric):
    if len(metric.split("/")) > 1:
        metric_name = metric.split("/")[1]
    else:
        metric_name = metric
    with open(directory + metric_name + '.yaml', 'a') as file:
        file.write('\n')
        file.write('####EVERYTHING ABOVE THIS LINE IS AUTOMATICALLY GENERATED - CHANGES WILL BE OVERWRITTEN####\n')
        file.write('---\n')
        file.write('## Put Links to queries or relevant reports below here. Use this format [Your_Name, Date]: www.some_link.com\n')
        file.write('---\n')
        file.write('\n')
        file.write('\n')
        file.write('---\n')
        file.write('## Known issues about handling or interpreting this probe go below.\n')
        file.write('Examples of common issues include:\n')
        file.write('* Inconsistency or unreliability of when the probe is recorded\n')
        file.write('* Commonly observed values that should be impossible\n')
        file.write('* Values that require special interpretation (e.g. 10,000 = timeout)\n')
        file.write('* Situations where the probe is triggered unexpectedly\n')
        file.write('---\n')
        file.write('\n')
        file.write('\n')
        file.write('---\n')
        file.write('## Common metrics that are computed with this probe and their interpretation / description\n')
        file.write('* Can also include names of BigQuery tables where the metric is stored.\n')
        file.write('---\n')
        file.write('\n')
        file.write('\n')
        file.write('---\n')
        file.write('## Other Notes\n')
        file.write('---\n')


def update_file_list(directory, endpoint, fields):
    """will create files for new probes and update existing files with latest info from the probe info service"""
    response = requests.get(endpoint)
    metrics_data = response.json()
    received_metrics = metrics_data.keys()
    files = listdir(directory)
    stored_metrics = [path.splitext(f)[0] for f in files]

    for m in received_metrics:
        if endpoint == FENIX_METRICS_ENDPOINT:
            metric_data = metrics_data.get(m).get('history')[-1]
            metric_name = m
        else:
            metric_data = metrics_data.get(m).get('history').get('nightly')[-1]
            metric_name = m.split("/")[1]
        # if file exists, read in user-edited data so its not overwritten
        if metric_name in stored_metrics:
            yaml = open(directory + metric_name + '.yaml', 'r')
            lines = yaml.readlines()
            to_save = []
            save_line = False
            for l in lines:
                # pretty hacky, just save all the stuff after the first --- line break :shrug:
                if l == '####EVERYTHING ABOVE THIS LINE IS AUTOMATICALLY GENERATED - CHANGES WILL BE OVERWRITTEN####\n':
                    save_line = True
                if save_line:
                    to_save.append(l)
            yaml.close()
            # update probe service-based data
            create_one_file(directory, m, metric_data, fields)
            # add back in user defined data
            with open(directory + metric_name + '.yaml', 'a') as file:
                for s in to_save:
                    file.write(s)
        # otherwise, create a new file
        else:
            create_one_file(directory, m, metric_data, fields)
            add_editable_fields_once(directory, m)

def build_files(endpoint, target_directory, fields):
    response = requests.get(endpoint)
    metrics = response.json()
    for k in metrics.keys():
        if endpoint == FENIX_METRICS_ENDPOINT:
            metric_data = metrics.get(k).get('history')[-1]
        else:
            metric_data = metrics.get(k).get('history').get('nightly')[-1]
        create_one_file(target_directory, k, metric_data, fields)
        add_editable_fields_once(target_directory, k)


# build_files(FIREFOX_DESKTOP_ENDPOINT, FIREFOX_DESKTOP_FILE_DIRECTORY, FIREFOX_DESKTOP_FIELDS)
# update_file_list(FIREFOX_DESKTOP_FILE_DIRECTORY, FIREFOX_DESKTOP_ENDPOINT, FIREFOX_DESKTOP_FIELDS)
# build_files(FENIX_METRICS_ENDPOINT, FENIX_FILE_DIRECTORY, FENIX_FIELDS)
# update_file_list(FENIX_FILE_DIRECTORY, FENIX_METRICS_ENDPOINT, FENIX_FIELDS)
