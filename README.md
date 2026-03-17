# Proof Gallery

This repo is set up for a GitHub Pages site that shows proof and payment images together in matching pairs.

## Files

- `index.html`, `styles.css`, `app.js`: the actual website
- `data/proofs.json`: the list of proof/payment pairs shown on the site
- `tools/add_proof.py`: adds a new proof/payment pair and updates the site data
- `tools/publish.py`: commits and pushes the latest changes to GitHub

## Turn on GitHub Pages

1. Push the `gh-pages` branch.
2. In your GitHub repo, open **Settings** > **Pages**.
3. Set the source to deploy from a branch.
4. Choose branch `gh-pages` and folder `/ (root)`.
5. Save the setting.

Your site URL will be:

`https://sarrwahhh.github.io/proofs/`

## Add a new proof set

Desktop window:

```powershell
python tools/add_proof.py
```

That opens a simple window where you click `Choose proof`, `Choose payment`, and then `Confirm and upload`.

Direct command:

```powershell
python tools/add_proof.py --proof "C:\path\to\proof.jpg" --payment "C:\path\to\payment.jpg" --title "Order 103"
```

Direct command and publish right away:

```powershell
python tools/add_proof.py --proof "C:\path\to\proof.jpg" --payment "C:\path\to\payment.jpg" --title "Order 103" --publish
```

If you confirm the publish step, or use `--publish`, the script will commit and push the update to GitHub for you.

If you want the old terminal-only behavior, run:

```powershell
python tools/add_proof.py --no-gui
```

## Preview locally

Because the site loads `data/proofs.json`, open it with a local server instead of double-clicking the HTML file:

```powershell
python -m http.server 8000
```

Then open:

`http://localhost:8000/`

## Publish updates manually

```powershell
python tools/publish.py --message "Update proof gallery"
```

GitHub Pages normally takes a minute or two to show the new version after each push.
