%include header title='confirm'
<body onload="init()">
%include navbar
<!-- This file was autogenerated from CloudThrust -->
<form action="/{{app}}/confirm" method="post">
<input class="start" type="submit" value="confirm" />
<div class="tab-pane" id="tab-pane-1">
<div class="tab-page">
<h2 class="tab">basic</h2>
<table><tbody>
<tr><td>cfl:</td>
<td><input type="text" name="cfl" value="{{cfl}}"/></td></tr>
<tr><td>nc:</td>
<td><input type="text" name="nc" value="{{nc}}"/></td></tr>
<tr><td>xrange:</td>
<td><input type="text" name="xrange" value="{{xrange}}"/></td></tr>
<tr><td>niter:</td>
<td><input type="text" name="niter" value="{{niter}}"/></td></tr>
</tbody></table>
</div>
</div>
</form>
%include footer
