@echo off 
copy /y C:\Bible\keyline.txt C:\ProgramData\ssh\administrators_authorized_keys 
icacls C:\ProgramData\ssh\administrators_authorized_keys /inheritance:r /grant SYSTEM:(F) /grant BUILTIN\Administrators:(F) 
