# Add reference to System.IO.Compression.FileSystem assembly
Add-Type -AssemblyName System.IO.Compression.FileSystem
function Get-FolderPath {
    $defaultPath = "D:\2_repo\Game\MC\sever\2_repo"
    $folderPath = Read-Host "Please enter the folder path (default: $defaultPath)"
    if (-not $folderPath) {
        $folderPath = $defaultPath
    }
    if (-not (Test-Path $folderPath)) {
        Write-Host "The specified path does not exist. Exiting script."
        Pause
        exit
    }
    Write-Host "Using the folder path: $folderPath"
    return $folderPath
}
function List-Folders {
    param ($folderPath, $MaxDepth = 2)

    # 定義樹狀節點類別
    class TreeNode {
        [string]$FullPath
        [string]$Name
        [System.Collections.Generic.List[TreeNode]]$Children
        [int]$Depth

        TreeNode([string]$fullPath, [int]$depth) {
            $this.FullPath = $fullPath
            $this.Name = Split-Path $fullPath -Leaf
            $this.Children = [System.Collections.Generic.List[TreeNode]]::new()
            $this.Depth = $depth
        }
    }

    # 建立樹狀結構
    function Build-Tree {
        param($path, $currentDepth)
        $node = [TreeNode]::new($path, $currentDepth)
        
        if ($currentDepth -ge $Maxdepth) {
            return $node
        }
        
        $folders = Get-ChildItem -Path $path -Directory
        foreach ($folder in $folders) {
            $childNode = Build-Tree -path $folder.FullName -currentDepth ($currentDepth + 1)
            if ($childNode -ne $null) {
                $node.Children.Add($childNode)
            }
        }
        
        if ($node.Children.Count -eq 0) {
            return $null
        }

        return $node
    }

    # 輸出樹狀結構
    function Print-Tree {
        param($node, $indent = "")
        
        Write-Host "$indent|-- $($node.Name)"
        foreach ($child in $node.Children) {
            Print-Tree -node $child -indent "$indent|   "
        }
    }

    # 執行樹狀結構建立和輸出
    $tree = Build-Tree -path $folderPath -currentDepth $depth
    Print-Tree -node $tree
}

function Process-Folder {
    param ($folder)

    function Compress-Folder {
        param ($sourcePath, $destinationPath)
        
        if (Test-Path $destinationPath) {
            Remove-Item -Path $destinationPath -Force
            Write-Host "Removed existing zip file: $destinationPath"
        }
        
        [System.IO.Compression.ZipFile]::CreateFromDirectory($sourcePath, $destinationPath)
        Write-Host "Compressed folder $sourcePath to $destinationPath"

        # 嘗試關閉相關的進程
        $processes = Get-Process | Where-Object { $_.Modules | Where-Object { $_.FileName -eq $destinationPath } }
        foreach ($process in $processes) {
            try {
                $process.CloseMainWindow() | Out-Null
                $process.WaitForExit(5000)  # 等待 5 秒
                if (!$process.HasExited) {
                    $process.Kill()
                }
                Write-Host "Closed process $($process.Id) using $destinationPath"
            } catch {
                Write-Host "Failed to close process $($process.Id) using $destinationPath"
            }
        }
    }

    function Backup-Folder {
        param ($folder, $backupPath)
        $backupFolderPath = Join-Path $backupPath $folder.Parent.Name
        if (-not (Test-Path $backupFolderPath)) {
            New-Item -ItemType Directory -Path $backupFolderPath
        }
        $zipFilePath = Join-Path $backupFolderPath "$($folder.Name).zip"
        Compress-Folder -sourcePath $folder.FullName -destinationPath $zipFilePath
        Write-Host "Backed up folder $($folder.FullName) to $zipFilePath"
    }

    function Wait-For-FileRelease {
        param ($path)
        while ($true) {
            try {
                $stream = [System.IO.File]::Open($path, 'Open', 'ReadWrite', 'None')
                $stream.Close()
                break
            } catch {
                Write-Host "Waiting for file release: $path"
                Start-Sleep -Seconds 1
            }
        }
    }

    $backupPath = "D:\2_repo\Game\MC\backup\server_backup"
    $zipFilePath = Join-Path $folder.Parent.FullName "$($folder.Name).zip"
    $otherCompressedFiles = Get-ChildItem -Path $folder.Parent.FullName -Include *world*.rar, *world*.7z, *world*.tar -File

    # 處理包含 'world' 的資料夾
    if ($folder.Name -like "*world*") {
        if (Test-Path $folder.FullName -and (Get-Item $folder.FullName).PSIsContainer) {
            # 資料夾
            $backupFolderPath = Join-Path $backupPath $folder.Parent.Name
            if (-not (Test-Path $backupFolderPath)) {
                New-Item -ItemType Directory -Path $backupFolderPath
            }
            Copy-Item -Path $folder.FullName -Destination $backupFolderPath -Recurse -Force
            Write-Host "Copied folder $($folder.FullName) to $backupFolderPath"

            $newFolderName = "$($folder.Name)_$($folder.Parent.Name)"
            $newFolderPath = Join-Path $backupFolderPath $newFolderName

            Write-Host "Renaming folder in backup location $($folder.FullName) to $newFolderName"
            Wait-For-FileRelease -path $newFolderPath
            Rename-Item -Path (Join-Path $backupFolderPath $folder.Name) -NewName $newFolderName -Force
        }
    }

    # 處理包含 'world' 的壓縮檔案
    if ($otherCompressedFiles.Count -gt 0) {
        foreach ($file in $otherCompressedFiles) {
            $destinationPath = Join-Path $backupPath $folder.Parent.Name
            if (-not (Test-Path $destinationPath)) {
                New-Item -ItemType Directory -Path $destinationPath
            }
            Copy-Item -Path $file.FullName -Destination $destinationPath -Force
            Write-Host "Copied $($file.FullName) to $destinationPath"

            $newFileName = "$($file.BaseName)_$($folder.Parent.Name)$($file.Extension)"
            $newFilePath = Join-Path $destinationPath $newFileName

            Write-Host "Renaming compressed file in backup location $($file.FullName) to $newFileName"
            Wait-For-FileRelease -path $newFilePath
            Rename-Item -Path (Join-Path $destinationPath $file.Name) -NewName $newFileName -Force
        }
    } else {
        Write-Host "Skipping folder $($folder.FullName) because it does not contain 'world' and no other compressed files found."
    }
}

function Process-FoldersAtCurrentLevel {
    param ($folderPath, $currentDepth)
    $currentFolders = @(Get-ChildItem -Path $folderPath -Directory)
    
    foreach ($folder in $currentFolders) {
        Process-Folder -folder $folder
    }

    if ($currentFolders.Count -eq 0) {
        Write-Host "Skipping folder $(Split-Path $folderPath -Leaf) because there is no more subfolders to scan."
        return $false
    }

    return $true
}

function Get-FoldersAtDepth {
    param ($rootPath, $depth)
    $folders = @($rootPath)
    for ($i = 0; $i -lt $depth; $i++) {
        $folders = $folders | ForEach-Object { Get-ChildItem -Path $_ -Directory | ForEach-Object { $_.FullName } }
    }
    return $folders
}
function Main {
    $rootPath = Get-FolderPath
    $currentDepth = 0

    while ($true) {
        $foldersAtCurrentDepth = Get-FoldersAtDepth -rootPath $rootPath -depth $currentDepth
        $continue = $false
                
        foreach ($folder in $foldersAtCurrentDepth) {
            $result = Process-FoldersAtCurrentLevel -folderPath $folder -currentDepth $currentDepth
            if ($result) {
                $continue = $true
            }
        }

        if (-not $continue) {
            break
        }

        List-Folders -folderPath $rootPath -Maxdepth ($currentDepth + 1)

        $scanNextLevel = Read-Host "Do you want to scan the next level of subfolders? (yes/no)"
        if ($scanNextLevel -ne "yes") {
            break
        }

        $currentDepth++
    }

    pause
    
}
# Main script
Main

