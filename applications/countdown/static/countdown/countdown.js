/**
 * Contador regresivo hasta la fecha objetivo (11 mar 2030 12:00 America/Santiago).
 * Actualiza días, horas, minutos y segundos cada segundo.
 */
(function () {
  var targetISO = window.COUNTDOWN_TARGET_ISO;
  if (!targetISO) return;

  var target = new Date(targetISO);
  var ids = {
    days: 'countdown-days',
    hours: 'countdown-hours',
    minutes: 'countdown-minutes',
    seconds: 'countdown-seconds'
  };

  function pad(n) {
    return n < 10 ? '0' + n : String(n);
  }

  function update() {
    var now = new Date();
    var diff = target - now;

    if (diff <= 0) {
      document.getElementById(ids.days).textContent = '0';
      document.getElementById(ids.hours).textContent = '00';
      document.getElementById(ids.minutes).textContent = '00';
      document.getElementById(ids.seconds).textContent = '00';
      return;
    }

    var totalSeconds = Math.floor(diff / 1000);
    var seconds = totalSeconds % 60;
    var totalMinutes = Math.floor(totalSeconds / 60);
    var minutes = totalMinutes % 60;
    var totalHours = Math.floor(totalMinutes / 60);
    var hours = totalHours % 24;
    var days = Math.floor(totalHours / 24);

    document.getElementById(ids.days).textContent = String(days);
    document.getElementById(ids.hours).textContent = pad(hours);
    document.getElementById(ids.minutes).textContent = pad(minutes);
    document.getElementById(ids.seconds).textContent = pad(seconds);
  }

  update();
  setInterval(update, 1000);
})();
