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

## License

This repo is under the [MIT License](LICENSE).
