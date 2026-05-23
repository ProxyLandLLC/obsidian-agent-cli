# Installation Guide

## What You Need First

Before installing the CLI, make sure the new PC has:

1. **Python 3.10 or newer**
   Open PowerShell and run:
   ```powershell
   python --version
   ```
   If you get an error or a version below 3.10, download Python from [python.org](https://www.python.org/downloads/) and install it. Check "Add Python to PATH" during setup.

2. **Obsidian** — the desktop app, installed and open.

3. **Local REST API plugin** installed inside Obsidian:
   - Open Obsidian → Settings → Community Plugins → Browse
   - Search for **"Local REST API"**
   - Install and Enable it
   - Go to its settings tab and copy your **API Key** — you'll need it later

---

## Step 1 — Get the Files onto the New PC

You don't need git. Just copy the folder.

**Easiest options:**

- **USB drive** — copy the entire `Obsidian CLI` folder to a USB stick, plug it into the new PC, drag it somewhere like `C:\Users\YourName\Documents\`
- **Cloud sync** — if you use OneDrive, Google Drive, or Dropbox, just put the folder there and it syncs automatically
- **Zip file over email/transfer** — right-click the `Obsidian CLI` folder → Send to → Compressed (zipped) folder, then send that zip to yourself and unzip it on the new PC

The folder just needs to exist somewhere on the new PC. It doesn't matter where.

---

## Step 2 — Install

Open PowerShell, navigate to wherever you put the folder, and run one command:

```powershell
cd "C:\Users\YourName\Documents\Obsidian CLI"
pip install -e .
```

> Replace the path with wherever you actually put the folder.

That's it. Python reads the project and wires up the `obsidian` command globally.

---

## Step 3 — Configure

Run the setup wizard:

```powershell
obsidian config init
```

It will ask you four things:

| Prompt | What to enter |
|--------|--------------|
| Vault path | The full path to your Obsidian vault folder, e.g. `C:\Users\YourName\Documents\MyVault` |
| Chief path | Just press Enter to accept the default (`Chief`) |
| API URL | Just press Enter to accept the default (`https://127.0.0.1:27123`) |
| API key | Paste the key you copied from Obsidian → Local REST API settings |

Your config is saved automatically. You won't need to do this again.

---

## Step 4 — Verify It Works

With Obsidian open, run:

```powershell
obsidian status
```

You should see something like:
```json
{"ok": true, "versions": {"obsidian": "1.x.x"}, "transport": "api"}
```

If you see `"ok": true` — you're done.

---

## If You Update the CLI Later

When new commands are added to the CLI on your main PC, just copy the updated `Obsidian CLI` folder to the new PC again (replacing the old one), then run:

```powershell
cd "C:\Users\YourName\Documents\Obsidian CLI"
pip install -e .
```

Your config is stored separately and won't be affected.

---

## Troubleshooting

**`obsidian` is not recognized as a command**
- Make sure Python is on your PATH. Re-run the Python installer and check "Add Python to PATH", then open a new PowerShell window and try again.

**`obsidian status` shows an error about the API**
- Make sure Obsidian is open.
- Make sure the Local REST API plugin is enabled (not just installed).
- Double-check your API key: Obsidian → Settings → Local REST API → copy the key → run `obsidian config set api_key YOUR_KEY`.

**Wrong vault path**
```powershell
obsidian config set vault_path "C:\Users\YourName\Documents\CorrectVaultName"
```
