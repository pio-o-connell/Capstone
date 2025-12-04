Param(
    [ValidateSet('postgres','sqlite','status')]
    [string]$Mode = 'status'
)

function Show-Usage {
    Write-Output "Usage: .\scripts\toggle_db.ps1 [postgres|sqlite|status]"
    Write-Output "Examples:"
    Write-Output "  .\scripts\toggle_db.ps1 postgres"
    Write-Output "  .\scripts\toggle_db.ps1 sqlite"
    Write-Output "  .\scripts\toggle_db.ps1 status"
}

switch ($Mode) {
    'postgres' {
        $env:USE_POSTGRES = '1'
        Write-Output "Switched to Postgres for this session (USE_POSTGRES=1)."
        break
    }
    'sqlite' {
        Remove-Item Env:\USE_POSTGRES -ErrorAction SilentlyContinue
        Remove-Item Env:\DATABASE_URL -ErrorAction SilentlyContinue
        Write-Output "Switched to SQLite for this session (USE_POSTGRES/DATABASE_URL removed)."
        break
    }
    'status' {
        Write-Output "USE_POSTGRES = $($env:USE_POSTGRES)"
        Write-Output "DATABASE_URL = $($env:DATABASE_URL)"
        break
    }
    Default {
        Show-Usage
    }
}
