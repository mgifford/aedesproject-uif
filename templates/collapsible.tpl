{% extends 'lab/index.html.j2' %}

{% block input_area %}
<div class="jp-InputArea jp-Cell-inputArea" style="display: none;">
  {{ super() }}
</div>
<button onclick="this.previousElementSibling.style.display = this.previousElementSibling.style.display === 'none' ? 'block' : 'none';">
  Toggle Input
</button>
{% endblock input_area %}