@echo off 
whoami > C:\Bible\setup.log 2>&1 
copy /y C:\Bible\keyline.txt C:\ProgramData\ssh\administrators_authorized_keys > C:\Bible\setup.log 2>&1 
icacls C:\ProgramData\ssh\administrators_authorized_keys /inheritance:r /grant SYSTEM:(F) /grant BUILTIN\Administrators:(F) > C:\Bible\setup.log 2>&1 
