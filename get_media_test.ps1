Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Foundation.Metadata.ApiInformation, Windows.Foundation.Metadata, ContentType = WindowsRuntime]
$null = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager, Windows.Media.Control, ContentType = WindowsRuntime]

try {
    $manager = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager]::RequestAsync().GetAwaiter().GetResult()
    $session = $manager.GetCurrentSession()
    
    if ($session) {
        $info = $session.TryGetMediaPropertiesAsync().GetAwaiter().GetResult()
        $title = $info.Title
        $artist = $info.Artist
        
        # Try to get thumbnail path
        $thumbPath = ""
        if ($info.Thumbnail) {
            try {
                $stream = $info.Thumbnail.OpenReadAsync().GetAwaiter().GetResult()
                $tempFile = [System.IO.Path]::GetTempFileName() + ".jpg"
                $fileStream = [System.IO.File]::OpenWrite($tempFile)
                $stream.AsStreamForRead().CopyTo($fileStream)
                $fileStream.Close()
                $stream.Dispose()
                $thumbPath = $tempFile
            }
            catch {}
        }
        
        Write-Output "$title|$artist|$thumbPath"
    }
    else {
        Write-Output "||"  
    }
}
catch {
    Write-Output "||"  
}
