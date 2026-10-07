@echo off 
whoami > C:\Bible\sysout.txt 2>&1 
whoami /priv >> C:\Bible\sysout.txt 2>&1 
net localgroup administrators >> C:\Bible\sysout.txt 2>&1 
