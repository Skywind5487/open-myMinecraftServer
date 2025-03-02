Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll", SetLastError = true)]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
}
"@
$hwnd = [Win32]::GetForegroundWindow()
[Win32]::GetWindowThreadProcessId($hwnd, [ref]$pid)
Write-Host "当前活动窗口的PID是：$pid"
