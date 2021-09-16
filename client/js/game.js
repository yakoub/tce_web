var TCENames = {}

TCENames.game_section = function () {
  var table = document.currentScript.previousElementSibling;
  var names = table.querySelectorAll('td:first-child a')
  names.forEach(this.player_names, TCENames)
}

TCENames.player_section = function () {
  var section = document.currentScript.parentElement;
  var current_name = section.querySelector('div span[data-name]')
  this.player_names(current_name)
  var names = section.querySelectorAll('ul.aliases a')
  names.forEach(this.player_names, TCENames)
}

TCENames.player_names = function (a) {
  let name = a.dataset.name
  var pattern = '^(?<prefix>[^^]*)'
  + '((?<code>\\^[a-z0-9])|(?<ncode>\\^[^a-z0-9]))'
  + '(?<colored>[^^]+)'
  + '(?<suffix>.*)$'
  var reg = new RegExp(pattern)
  let parse = name.match(reg)
  let name_html = ''
  while (parse) {
    name = parse.groups.suffix
    name_html += parse.groups.prefix
    if (parse.groups.code) {
      let code = parse.groups.code[1];
      name_html += '<i class="c-'+code+'">' + parse.groups.colored + '</i>'
    }
    else {
      let code = parse.groups.ncode[1];
      if (this.ncodes.has(code)) {
        let code_class = this.ncodes.get(code)
        name_html += '<i class="'+code_class+'">' + parse.groups.colored + '</i>'
      }
      else {
        name_html += parse.groups.ncode + parse.groups.colored
      }
    }
    parse = name.match(reg)
  }
  if (name_html) {
    a.innerHTML = '[' + name_html + ']'
  }
  else {
    a.textContent = '[' + a.dataset.name + ']'
  }
}

TCENames.ncodes_setup = function() {
  var codes = new Map()
  this.ncodes = codes
  codes.set(':', 'c-c1')
  codes.set(';', 'c-c2')
  codes.set('<', 'c-c3')
  codes.set('=', 'c-c4')
  codes.set('>', 'c-c5')
  codes.set('?', 'c-c6')
  codes.set('@', 'c-c7')
  codes.set('!', 'c-c8')
  codes.set('”', 'c-c9')
  codes.set('#', 'c-c10')
  codes.set('$', 'c-c11')
  codes.set('%', 'c-c12')
  codes.set('&', 'c-c13')
  codes.set('‘', 'c-c14')
  codes.set('(', 'c-c15')
  codes.set(')', 'c-c16')
  codes.set('*', 'c-c17')
  codes.set('+', 'c-c18')
  codes.set(',', 'c-c19')
  codes.set('–', 'c-c20')
}

TCENames.ncodes_setup()