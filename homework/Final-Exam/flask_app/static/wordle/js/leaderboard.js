var times = document.querySelectorAll('.leaderboard-item span');
times.forEach( (sp) => {
  sp.innerHTML = formatTime(sp.innerHTML);
});

function addZeroPadding(num) {
  if (num <= 9) {
      return String("0" + num);
  }
  return String(num);
}

function formatTime(seconds) {
  var hour = addZeroPadding(Math.floor(seconds / 3600));
  var minute = addZeroPadding(Math.floor((seconds - hour * 3600) / 60));
  var seconds = addZeroPadding(seconds - (hour * 3600 + minute * 60));

  return String(hour + ':' + minute + ':' + seconds);
}