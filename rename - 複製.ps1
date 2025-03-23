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

    
    function Get-ServerPort {
        param ($serverPropertiesPath)
        $serverPort = Select-String -Path $serverPropertiesPath -Pattern "^server-port=" | ForEach-Object { $_.Line.Split('=')[1].Trim() }
        if (-not $serverPort) {
            Write-Host "Unable to find server-port in $serverPropertiesPath."
            return $null
        }
        return $serverPort
    }
    
    function Get-Version {
        param ($folder)
        $possibleJarNames = @('server.jar', 'paper.jar', 'spigot.jar')
        
        foreach ($jarName in $possibleJarNames) {
            $serverJarPath = Join-Path $folder.FullName $jarName
            if (Test-Path $serverJarPath) {
                break
            }
        }
        if (-not (Test-Path $serverJarPath)) {
            Write-Host "Unable to find server jar in $folder ."
        }
        $version = ""
        try {
            $zip = [System.IO.Compression.ZipFile]::OpenRead($serverJarPath)
            $entry = $zip.Entries | Where-Object { $_.FullName -eq "version.json" }
            if ($entry) {
                $versionStream = $entry.Open()
                $reader = New-Object System.IO.StreamReader($versionStream)
                $versionJson = $reader.ReadToEnd()
                $reader.Close()
                $versionStream.Close()
                $zip.Dispose()
                $jsonObject = $versionJson | ConvertFrom-Json
                $version = $jsonObject.id
            } else {
                return $null
            }
        } catch {
            return $null
        }
        return $version
    }
    
    function Get-VersionType {
        param ($folder)
        $versionType = "vanilla"
        if (Test-Path (Join-Path $folder.FullName 'fabric-server-launcher.properties')) {
            $versionType = "fabric"
        } elseif (Get-ChildItem -Path $folder.FullName -Recurse -File | Where-Object { $_.Name -like "*forge*" }) {
            $versionType = "forge"
        } elseif (Get-ChildItem -Path $folder.FullName -Recurse -File | Where-Object { $_.Name -like "*paper*" }) {
            $versionType = "paper"
        } elseif (Get-ChildItem -Path $folder.FullName -Recurse -File | Where-Object { $_.Name -like "*spigot*" }) {
            $versionType = "spigot"
        }
        return $versionType
    }
    
    function Rename-Folder {
        param ($folder, $newName, $newFolderPath)
        try {
            $openFiles = Get-Process | Where-Object { $_.Modules | Where-Object { $_.FileName -like "$($folder.FullName)*" } }
            if ($openFiles) {
                Write-Host "Some files in the folder are currently in use. Please close them and try again."
                return
            }
        } catch {
            return
        }
    
        $waitTime = 5
        for ($i = $waitTime; $i -gt 0; $i--) {
            Start-Sleep -Seconds 1
        }
    
        try {
            Rename-Item -Path $folder.FullName -NewName $newName -Force
        } catch {
            Write-Host "Unable to rename folder $folder. Error: $_"
        }
    }
    
    function Parse-FolderName {
        param ($folderName)
        if ($folderName -match "^(.*?)(_([^_]+)){3}$") {
            return @{
                BaseName = $matches[1]
                ExistingVersion = $matches[3]
                ExistingPort = $matches[4]
                ExistingType = $matches[5]
            }
        } else {
            return @{
                BaseName = $folderName
                ExistingVersion = ""
                ExistingPort = ""
                ExistingType = ""
            }
        }
    }
    
    $parsedName = Parse-FolderName -folderName $folder.Name

    $serverPropertiesPath = Join-Path $folder.FullName 'server.properties'
    if (-not (Test-Path $serverPropertiesPath)) {
        return
    }

    $serverPort = Get-ServerPort -serverPropertiesPath $serverPropertiesPath
    if (-not $serverPort) {
        return
    }

    $version = Get-Version -folder $folder
    if (-not $version) {
        return
    }

    $versionType = Get-VersionType -folder $folder

    $newName = "$($parsedName.BaseName)`_$version`_$serverPort`_$versionType"
    $newFolderPath = Join-Path $folder.Parent.FullName $newName

    if ($folder.Name -eq $newName) {
        Write-Host "Folder $folder is same as $newName. Skipping."
        return
    } elseif (Test-Path $newFolderPath) {
        return
    }

    Rename-Folder -folder $folder -newName $newName -newFolderPath $newFolderPath

    Write-Host "Renamed folder $folder to $newName."
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

