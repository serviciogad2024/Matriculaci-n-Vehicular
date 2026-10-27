(function () {
  var sel = document.getElementById('dig');
  if (!sel) return;
  var months = {1:'febrero',2:'marzo',3:'abril',4:'mayo',5:'junio',6:'julio',7:'agosto',8:'septiembre',9:'octubre',0:'noviembre'};
  var idx = {1:1,2:2,3:3,4:4,5:5,6:6,7:7,8:8,9:9,0:10};
  var out = document.getElementById('res');
  sel.addEventListener('change', function () {
    var v = sel.value;
    if (v === '') { out.textContent = ''; return; }
    var now = new Date().getMonth();
    var d = idx[v] - now;
    var msg = 'Tu mes de matriculación es ' + months[v] + '. ';
    if (d === 0) msg += 'Es este mes: aprovéchalo antes de que termine.';
    else if (d > 0) msg += 'Faltan ' + d + (d === 1 ? ' mes.' : ' meses.');
    else msg += 'Ya pasó este año: revisa recargos y multas pendientes.';
    out.textContent = msg + ' Diciembre es para rezagados, con recargos.';
  });
})();
