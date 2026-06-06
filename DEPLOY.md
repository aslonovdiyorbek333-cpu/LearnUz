Quick deploy instructions

1. Prepare SSH keys

- On your local machine:
  - `ssh-keygen -t ed25519 -C "your_email@example.com"`
  - Add the public key (`~/.ssh/id_ed25519.pub`) to GitHub (Settings → SSH and GPG keys).
  - Add the same public key to PythonAnywhere (Account → SSH keys) or use PythonAnywhere web console.

2. Run local deploy script (PowerShell)

- In project root:

```powershell
./deploy.ps1
```

- The script will ask for branch, remote, commit message, PythonAnywhere username, remote repo folder and virtualenv path.

3. Or run remote deploy script (Linux/macOS)

- Set env var `PA_USER` first:

```bash
export PA_USER=yourusername
./scripts/deploy_remote.sh main origin ~/LearnUz_prj /home/yourusername/.virtualenvs/venv
```

4. GitHub Actions (automatic on push)

- Add three secrets to your GitHub repo: `PA_SSH_PRIVATE_KEY` (your private key), `PA_USERNAME`, `PA_REPO_PATH`, `PA_VENV_PATH`.
- Push to `main` and the workflow will deploy.

Security note

- Use a time-limited or dedicated deploy key. Remove it after use if you are not comfortable keeping it.
