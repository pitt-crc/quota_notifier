{% if not obj.display %}
:orphan:

{% endif %}

{{ obj.name|strip_leading_import }}
{{ "=" * obj.name|length }}

{% if obj.type == "package" %}
.. toctree::
   :titlesonly:
   :hidden:
   :glob:

   */index

{% endif %}

{% if obj.docstring %}
{{ obj.docstring }}
{% endif %}

{% set visible_children = obj.children|selectattr("display")|rejectattr("imported")|list %}
{% set visible_classes = visible_children|selectattr("type", "equalto", "class")|list %}
{% set visible_functions = visible_children|selectattr("type", "equalto", "function")|list %}
{% set visible_attributes = visible_children|selectattr("type", "equalto", "data")|list %}

{% if visible_functions %}
Module Functions
----------------

{% for function in visible_functions %}
.. autofunction:: {{ function.id }}

{% endfor %}
{% endif %}

{% if visible_classes %}
Module Classes
--------------

{% for class in visible_classes %}
.. autoclass:: {{ class.id }}
   :members:

{% endfor %}
{% endif %}
