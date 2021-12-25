# Repository Status for Scikit-learn

[Live webpage](https://thomasjpfan.github.io/sklearn-repo-status/)

Auto updating website that tracks closed & open issues/PRs.

## Running locally

0. Setup venv
1. Install requirements

```bash
pip install -r requirements
```

2. Create a personal access token and set it to `GITHUB_TOKEN`.

3. Run the following to call the GitHub API for repo information and cache the results into `cache.json`.

```bash
python make.py cache.json dist
```

4. Open `dist/index.html` to see the rendered page.

## How to setup for another repo?

1. Change `assets/logo.svg` to your logo.
2. Pass in `--repo` into the `make.py` command:

```python
python make.py cache.json dist --repo scikit-learn/scikit-learn
```

## Testing

If you already called the GitHub API once and cached the results, then you can pass
`--cache-only` to build without querying the GitHub API:

```python
python make.py cache.json dist --only-cache
```

## License

This repo is under the [MIT License](LICENSE).
