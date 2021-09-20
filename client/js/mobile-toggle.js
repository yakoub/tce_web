document.addEventListener('DOMContentLoaded', function(event) {
  let main = document.querySelector('#page > main')
  let sidebar = document.querySelector('#page > aside')
  document.querySelector('#page nav select').addEventListener('change', function(event) {
    if (this.value == 'stats') {
      main.style.display = 'none'
      sidebar.style.display = 'block'
    }
    else {
      main.style.display = 'block'
      sidebar.style.display = 'none'
    }
  });
});
