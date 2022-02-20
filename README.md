# Repository Status for Scikit-learn

[Live webpage](https://thomasjpfan.github.io/sklearn-repo-status/)

Auto updating website that tracks closed & open issues/PRs on [scikit-learn/scikit-learn](https://github.com/scikit-learn/scikit-learn/).

## Running locally

0. Setup a virtual environment.
1. Install requirements

```bash
pip install -r requirements
```

2. Create a personal access token and set it to `GITHUB_TOKEN`.

3. Run the following to call the GitHub API for repo information, cache the results into `cache.json`, and place the website into a `dist` directory.

```bash
python make.py cache.json dist
```

4. Open `dist/index.html` to see the rendered page.

## How to setup for another repo?

1. Add your logo into `assets` directory. You can use another logo as long as it is in the `assets` directory.
2. Pass in `--repo` into the `make.py` command. Use `--logo` if your logo has a different filename.

```python
python make.py cache.json dist \
    --repo scikit-learn/scikit-learn --logo logo.svg
```
3. **Extra**. To use Github Actions to auto generate the webpage update `.github/workflows/build.yaml` by passing in your `--repo`.

## Testing

If you already called the GitHub API once and cached the results, then you can pass
`--cache-only` to build without querying the GitHub API:

```python
python make.py cache.json dist --only-cache
```

## License

This repo is under the [MIT License](LICENSE).
