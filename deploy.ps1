Param()

# Simple PowerShell deploy script
Write-Host "Starting deploy script..." -ForegroundColor Cyan

function Exec($cmd) {
    Write-Host "> $cmd" -ForegroundColor Yellow
    $proc = Start-Process -FilePath powershell -ArgumentList "-NoProfile -Command $cmd" -Wait -PassThru -NoNewWindow
    return $proc.ExitCode
}

$branch = Read-Host "Branch (default: main)"
if ([string]::IsNullOrWhiteSpace($branch)) { $branch = 'main' }
$remote = Read-Host "Git remote (default: origin)"
if ([string]::IsNullOrWhiteSpace($remote)) { $remote = 'origin' }
$commitMsg = Read-Host "Commit message (default: Deploy changes)"
if ([string]::IsNullOrWhiteSpace($commitMsg)) { $commitMsg = 'Deploy changes' }

Write-Host "Committing and pushing to $remote/$branch..." -ForegroundColor Green
git add -A
git commit -m "$commitMsg" 2>$null
git push $remote $branch

$pa_user = Read-Host "PythonAnywhere username (eg. yourusername)"
$repoPath = Read-Host "Remote repo folder (eg. ~/LearnUz_prj)"
$venv = Read-Host "Virtualenv path on server (eg. /home/yourusername/.virtualenvs/venv)"

if ([string]::IsNullOrWhiteSpace($pa_user) -or [string]::IsNullOrWhiteSpace($repoPath) -or [string]::IsNullOrWhiteSpace($venv)) {
    Write-Host "Missing information — aborting." -ForegroundColor Red
    exit 1
}

$remoteCmd = "cd $repoPath; source $venv/bin/activate; git pull $remote $branch; pip install -r requirements.txt; python manage.py migrate --noinput; python manage.py collectstatic --noinput; touch /var/www/${pa_user}_pythonanywhere_com_wsgi.py"

Write-Host "Connecting to PythonAnywhere and running remote commands..." -ForegroundColor Green
    ssh "$pa_user@ssh.pythonanywhere.com" "$remoteCmd"
    Write-Host "Deploy finished. Check your site and logs on PythonAnywhere." -ForegroundColor Cyan
