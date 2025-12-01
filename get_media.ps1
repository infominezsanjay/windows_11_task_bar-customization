
# Load WinRT Types
[void][Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager, Windows.Media.Control, ContentType = WindowsRuntime]

async function Get-MediaInfo {
    $manager = await [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager]::RequestAsync()
    $session = $manager.GetCurrentSession()
    
    if ($session) {
        $info = await $session.TryGetMediaPropertiesAsync()
        Write-Output "$($info.Title)|$($info.Artist)"
    } else {
        Write-Output "No Music|"
    }
}

# Helper to run async in PS 5.1 (which is default on Win 11 usually, but let's assume 7 or just use .GetAwaiter().GetResult())
$manager = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager]::RequestAsync().GetAwaiter().GetResult()
$session = $manager.GetCurrentSession()

if ($session) {
    $info = $session.TryGetMediaPropertiesAsync().GetAwaiter().GetResult()
    Write-Output "$($info.Title)|$($info.Artist)"
} else {
    Write-Output "No Music|"
}
