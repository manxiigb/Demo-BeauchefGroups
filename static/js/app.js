// Comportamiento mínimo: todo funciona sin JS; esto solo mejora la experiencia.
(function () {
  // Oculta los avisos (messages de Django) después de unos segundos.
  document.querySelectorAll('.toast').forEach(function (t, i) {
    setTimeout(function () { t.classList.add('ocultar'); }, 4200 + i * 400);
    setTimeout(function () { t.remove(); }, 4600 + i * 400);
  });
  // Casilla «Post-its del tablero» de la barra de demo (recuerda la preferencia).
  var pi = document.getElementById('toggle-pi');
  if (pi) {
    try { pi.checked = localStorage.getItem('show-pi') === '1'; } catch (e) {}
    document.body.classList.toggle('show-pi', pi.checked);
    pi.addEventListener('change', function () {
      document.body.classList.toggle('show-pi', pi.checked);
      try { localStorage.setItem('show-pi', pi.checked ? '1' : '0'); } catch (e) {}
    });
  }
})();
