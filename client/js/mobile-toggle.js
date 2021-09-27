document.addEventListener('DOMContentLoaded', function(event) {
  let page = document.querySelector('#page')
  let navigation = document.querySelector('#page nav select')
  let current = navigation.value

  navigation.addEventListener('change', function(event) {
    page.children[current].classList.add('not-shown')
    current = this.value
    page.children[current].classList.remove('not-shown')
  });
});
