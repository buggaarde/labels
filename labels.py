#! /usr/local/bin/python3

import click
import os
import requests as r
import matplotlib as mpl
import json


@click.command()
@click.option(
    "--token", "-t", default="MY_GITHUB_TOKEN", show_default="MY_GITHUB_TOKEN"
)
@click.option(
    "--suffix", "-s", default="", help="suffix the specified labels with this option"
)
@click.option(
    "--prefix", "-p", default="", help="prefix the specified labels with this option"
)
@click.option(
    "--description",
    "-d",
    default="",
    help='special forms are: {}, {p}, {s}, {ps}, which resolve to the label value, and either prefixed, suffixed or both, respectively.\nE.g. "{} {p} {s} {ps}"\n-> "LABEL prefixLABEL LABELsuffix prefixLABELsuffix"',
)
@click.option(
    "--color",
    "-c",
    default="#FFFAFA",
    help="can either be a hexcode or any named color in the CSS4 standard",
    show_default="#FFFAFA",
)
@click.option(
    "--update", "-u", is_flag=True, help="flag if existing labels should be updated"
)
@click.option("--is_json", "-j", is_flag=True, help="flag if input is a json-file")
@click.option(
    "--repo", "-r", required=True, help='a repo is of the form "owner/repository"'
)
@click.argument("labels_or_json", nargs=-1)
def main(
    labels_or_json, repo, is_json, color, update, description, prefix, suffix, token
):
    """Automate label creation on your GitHub projects

    Either specify the labels you want created directly, or read from json-file. 
    Reading from json will ignore all other options and only use what is read from file
    """

    if "/" not in repo:
        print('error: a repo is of the form "owner/repository"')
        return

    token = os.environ.get(token, "MISSING_TOKEN")
    if token == "MISSING_TOKEN":
        print(
            "error: MISSING TOKEN. --token must be the name of the environment variable containing the GitHub token"
        )
        return

    if is_json:
        j = open(labels_or_json[0])
        labels = json.load(j)["labels"]
        j.close()
    else:
        if color.lower() in mpl.colors.CSS4_COLORS.keys():
            color = mpl.colors.CSS4_COLORS[color.lower()]

        if not color.startswith("#"):
            color = ("#" + color).upper()

        labels = [
            {
                "name": f"{prefix}{lbl}{suffix}",
                "color": color[1:],
                "description": description.replace("{}", f"{lbl}")
                .replace("{s}", f"{lbl}{suffix}")
                .replace("{p}", f"{prefix}{lbl}")
                .replace("{ps}", f"{prefix}{lbl}{suffix}"),
            }
            for lbl in labels_or_json
        ]

    headers = {
        "Authorization": "token " + token,
        "Accept": "application/vnd.github.symmetra-preview.json",
    }

    request = r.post
    request_string = f"https://api.github.com/repos/{repo}/labels"

    curr_resp = json.loads(r.get(request_string, headers=headers).content)
    current_labels = [c["name"] for c in curr_resp]

    for l in labels:
        req_string = request_string
        req = request
        if update and l["name"] in current_labels:
            print(f'Label {l["name"]} already exists. Updating instead')
            req = r.patch
            req_string = request_string + f'/{l["name"]}'
        if not update and l["name"] in current_labels:
            print(f'Label {l["name"]} already exists. To update use flag "--update"')
            print("Skipping...")
            continue

        response = req(req_string, json=l, headers=headers)

        if response.status_code == 201:
            print(f'Created label {l["name"]} successfully')
            continue
        if response.status_code == 200:
            print(f'Updated label {l["name"]} successfully')
            continue

        print(
            f'Error creating label {l["name"]} with status code {response.status_code}:'
        )
        msg = json.loads(response.content)["message"]
        url = json.loads(response.content)["documentation_url"]
        print(f"{msg}: See {url}")


if __name__ == "__main__":
    main()
