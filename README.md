# labels

Automate label creation on your GitHub projects.

Either specify the labels you want created directly, or read from json-file. Reading from json will ignore all other options and only use what is read from file.

## Usage

``` bash
labels labels_or_json --repo "owner/repository" [flags] [options]
```

In order for `labels` to be a valid executable, make sure to move `labels.py` to `/usr/local/bin/labels` after making it executable. I.e.

``` bash
sudo chmod +x ./labels.py

sudo cp ./labels.py /usr/local/bin/labels
```

## Overview

`labels_or_json` is either a list of labels you want created, or a file containing json specifying the labels. If you want to read json from file, set the `--is_json`/`-j` flag.

`--repo`/`-r` specifies the repository in which you wish to create/update labels.

### Flags

`--is_json`/`-j` flags whether or not the `labels_or_json` is a list of labels or a file specifying the labels. See [the GitHub API](https://developer.github.com/v3/issues/labels/#create-a-label) for the expected json-data.

`--update`/`-u` flags whether existing labels should be skipped or updated with new information.

### Options

`--color`/`-c` specifies the color of the labels. Can either be a hex value or any [named color in the CSS4-standard](https://www.w3.org/TR/css-color-4/#named-colors). Defaults to `#FFFAFA`.

`--prefix`/`-p` prefixes each label from the `labels_or_json` argument.

`--suffix`/`-s` suffixes each label from the `labels_or_json` argument.

`--description`/`-d` is the description of each label. In order facilitate dynamic creation of descriptions based on the label name, four special forms can be used: `{}`, `{p}`, `{s}`  and `{ps}`. They resolve to the label name, prefixed label name, suffixed label name and both pre- and suffixed label name, respectively.

`--token`/`-t` sets the name of the environment variable which contains the GitHub authorization token. Defaults to `MY_GITHUB_TOKEN`.

## Requirements
Requires python 3.6+ and `requests`, `click` and `matplotlib`.

## Examples

### Manual specification of labels

``` bash
labels 0 1 2 3 5 8 --update -r "my/repository" -c "hotpink" -p "f" -d "{} {p} {s} {ps}"
```
The above will create the labels `f0 f1 f2 f3 f5` and `f8` in the repository `my/repository`. If any labels already exist, they will be updated to be equal to the new information. All labels will be colored hotpink and have the description `n fn n fn` -- where `n` is the label name -- since `f` is the prefix, and there is no suffix. Finally, the labels will be created with the authorization token behind the environment variable `MY_GITHUB_TOKEN`.

### Creating labels from json

If we have the file `labels.json`:
``` json
{
	"labels": [
		{
			"name": "label1",
			"color": "ff0000",
			"description": "a red label"
		},
		{
			"name": "label2",
			"color": "00ff00",
			"description": "a green label"
		},
		{
			"name": "label3",
			"color": "0000ff",
			"description": "a blue label"
		}
	]
}
```

The command
``` bash
labels labels.json --is_json -r "my/repository" -t "GITHUB_TOKEN" -p "dont use"
```
will read the three labels from `labels.json` and create them in "my/repository" accordingly. The creation is authorized by the token behind the environment variable `GITHUB_TOKEN`. Since `--update` is not flagged, if any of the three labels already exist they will be skipped. Finally, since `--is_json` is flagged the prefix option is ignored.
