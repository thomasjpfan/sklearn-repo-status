import sys
import json
import os
from itertools import groupby, product
from collections import defaultdict
import argparse
from pathlib import Path
from collections import defaultdict
from shutil import copyfile

from jinja2 import Template
from github import Github
from datetime import datetime, timezone, timedelta
import matplotlib.pyplot as plt


def by_pulls_issues(all_items, key):
    by_pulls = defaultdict(int)
    by_issues = defaultdict(int)

    by_attr = groupby(
        all_items, lambda x, key=key: (getattr(x, key).year, getattr(x, key).month)
    )
    for key, items in by_attr:
        for item in items:
            if "/pull/" in item.html_url:
                by_pulls[f"{key[0]}-{key[1]}"] += 1
            else:
                by_issues[f"{key[0]}-{key[1]}"] += 1

    return {"by_pulls": by_pulls, "by_issues": by_issues}


def create_graph(
    data,
    keys_to_show,
    path,
    by_key,
    closed_label,
):
    x_range = list(range(len(keys_to_show)))
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    created = [data["created_bys"][by_key].get(key, 0) for key in keys_to_show]
    closed = [data["closed_bys"][by_key].get(key, 0) for key in keys_to_show]

    ax.plot(x_range, created, "o-", label="Opened", lw=3, markersize=6)
    ax.plot(x_range, closed, "D-", label=closed_label, lw=3, markersize=6)
    ax.set_ylim(0, None)
    ax.set_xticks(x_range)

    ax.set_xticklabels(
        [key if i % 2 == 0 else "" for i, key in enumerate(keys_to_show)],
        rotation=45,
        fontdict={"size": 18},
    )
    ax.tick_params(axis="y", labelsize=24)
    ax.set_ylabel("Count", fontdict={"size": 28})
    ax.legend(loc="lower right", fontsize=22)
    ax.grid(axis="y")
    fig.savefig(path, bbox_inches="tight")


def load_data(repo, now, cache, only_cache):
    if only_cache:
        if not cache.exists():
            print("only-cache==True but cache does not exist")
            sys.exit(1)
        with cache.open("r") as f:
            return json.load(f)

    print("Getting data from GitHub")
    first_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    previous_month = (first_this_month - timedelta(days=10)).replace(day=1)

    if not cache.exists():
        # load in 2 years worth of data if there is no cache
        since = previous_month.replace(year=now.year - 2)
    else:
        # There is a cache, only need to update the previous month + this month
        since = previous_month

    issues = repo.get_issues(state="all", since=since)
    all_issues = list(issues)
    new_data = {
        "created_bys": by_pulls_issues(all_issues, "created_at"),
        "closed_bys": by_pulls_issues(
            (i for i in all_issues if i.closed_at is not None), "closed_at"
        ),
    }

    if not cache.exists():
        print("Saving to cache")
        with cache.open("w") as f:
            json.dump(new_data, f)
        return new_data

    print("Updating cache")
    # cache exist -> need to update data and cache
    now_str = f"{now.year}-{now.month}"
    previous_str = f"{previous_month.year}-{previous_month.month}"

    # Update cache data
    with cache.open("r") as f:
        data = json.load(f)
    keys = product(
        ["created_bys", "closed_bys"],
        ["by_pulls", "by_issues"],
        [previous_str, now_str],
    )
    for key1, key2, time_key in keys:
        data[key1][key2][time_key] = new_data[key1][key2].get(time_key, 0)

    with cache.open("w") as f:
        json.dump(data, f)
    return data


def get_past_time_keys(now, num):
    cur_year = now.year
    cur_month = now.month

    output = []
    for _ in range(num):
        output.append(f"{cur_year}-{cur_month}")
        if cur_month > 1:
            cur_month -= 1
        else:
            cur_month = 12
            cur_year -= 1
    return list(reversed(output))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cache", help="Cache Folder", type=str)
    parser.add_argument("dist", help="Distribution folder", type=str)
    parser.add_argument(
        "--github_token",
        help="GitHub Token",
        type=str,
        default=os.environ.get("GITHUB_TOKEN"),
    )
    parser.add_argument(
        "--repo", help="Repo to query", type=str, default="scikit-learn/scikit-learn"
    )
    parser.add_argument("--logo", help="logo", type=str, default="logo.svg")
    parser.add_argument(
        "--only-cache", help="Only use cached data", action="store_true"
    )

    args = parser.parse_args()
    cache = Path(args.cache)
    assets = Path("assets")

    logo_path = assets / args.logo
    if not logo_path.exists():
        print(f"--logo {args.logo} must be in the assets directory")
        sys.exit(1)

    gh = Github(args.github_token)
    sk_repo = gh.get_repo(args.repo)

    now = datetime.now(tz=timezone.utc)

    data = load_data(sk_repo, now, cache, args.only_cache)

    # Use the last 19 months (18 complete months and the most recent one)
    keys_to_show = get_past_time_keys(now, 20)

    last_4_keys = keys_to_show[-5:-1]
    current_key = keys_to_show[-1]
    template_data = {
        "repo": args.repo,
        "logo": logo_path.name,
        "current_month": now.strftime("%B"),
        "current_year": now.year,
        "current_datetime": now.strftime("%B %d, %Y"),
        "current_issues_closed": data["closed_bys"]["by_issues"].get(current_key, 0),
        "current_issues_opened": data["created_bys"]["by_issues"].get(current_key, 0),
        "current_pulls_closed": data["closed_bys"]["by_pulls"].get(current_key, 0),
        "current_pulls_opened": data["created_bys"]["by_pulls"].get(current_key, 0),
        "previous_months": [
            datetime.strptime(key, "%Y-%m").strftime("%b") for key in last_4_keys
        ],
        "previous_issues_closed": [
            data["closed_bys"]["by_issues"].get(key, 0) for key in last_4_keys
        ],
        "previous_issues_opened": [
            data["created_bys"]["by_issues"].get(key, 0) for key in last_4_keys
        ],
        "previous_pulls_closed": [
            data["closed_bys"]["by_pulls"].get(key, 0) for key in last_4_keys
        ],
        "previous_pulls_opened": [
            data["created_bys"]["by_pulls"].get(key, 0) for key in last_4_keys
        ],
    }

    template_data["previous_issues_delta"] = [
        "{0:+}".format(o - c)
        for o, c in zip(
            template_data["previous_issues_opened"],
            template_data["previous_issues_closed"],
        )
    ]
    template_data["previous_pulls_delta"] = [
        "{0:+}".format(o - c)
        for o, c in zip(
            template_data["previous_pulls_opened"],
            template_data["previous_pulls_closed"],
        )
    ]
    template_data["current_issues_delta"] = "{0:+}".format(
        template_data["current_issues_opened"] - template_data["current_issues_closed"]
    )
    template_data["current_pulls_delta"] = "{0:+}".format(
        template_data["current_pulls_opened"] - template_data["current_pulls_closed"]
    )

    dist = Path(args.dist)
    dist.mkdir(exist_ok=True)

    dist_asset = dist / "assets"
    dist_asset.mkdir(exist_ok=True)

    issues_img_path = dist_asset / "issues.svg"
    pulls_img_path = dist_asset / "pulls.svg"

    create_graph(
        data,
        keys_to_show[:-1],
        issues_img_path,
        "by_issues",
        "Closed",
    )
    create_graph(
        data,
        keys_to_show[:-1],
        pulls_img_path,
        "by_pulls",
        "Merged | Closed",
    )

    with (assets / "index.html.j2").open("r") as f:
        template = Template(f.read())

    output = template.render(**template_data)

    index_path = dist / "index.html"
    index_path.write_text(output)

    # move assets to dist
    copyfile(logo_path, dist_asset / logo_path.name)
    copyfile(cache, dist_asset / cache.name)
