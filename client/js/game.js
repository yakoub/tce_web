var TCENames = {}

TCENames.game_section = function () {
  var section = document.currentScript.parentElement;
  var names = section.querySelectorAll('table td:first-child a')
  names.forEach(this.player_names, TCENames)

  var gametype = section.querySelector('header.highlighted .gametype span')
  var types_map = section.dataset.hasOwnProperty('tce') ? this.tce_types_map : this.types_map
  if (types_map.has(gametype.dataset.type)) {
    gametype.textContent = types_map.get(gametype.dataset.type)
  }
  var hostname = section.querySelector('header.highlighted .hostname span')
  this.player_names(hostname)
}

TCENames.player_statistics = function () {
  var section = document.currentScript.parentElement;
  var names = section.querySelectorAll('ul a')
  names.forEach(this.player_names, TCENames)
}

TCENames.player_page = function () {
  var section = document.currentScript.parentElement;
  var current_name = section.querySelector('header span[data-name]')
  this.player_names(current_name)
}

TCENames.statistics_section = function () {
  var section = document.currentScript.parentElement;
  var names = section.querySelectorAll('table.players td:first-child a')
  names.forEach(this.player_names, TCENames)
}

TCENames.player_names = function (a) {
  let name = a.dataset.name
  let name_html = window.localStorage.getItem('name-html-' + name)
  if (name_html) {
    a.innerHTML = '[' + name_html + ']'
    return
  }
  if (window.localStorage.getItem('name-plain-' + name)) {
    a.textContent = '[' + a.dataset.name + ']'
    return
  }

  var pattern = '^(?<prefix>[^^]*)'
  + '((?<code>\\^[a-z0-9])|(?<ncode>\\^[^a-z0-9]))'
  + '(?<colored>[^^]+)'
  + '(?<suffix>.*)$'
  var reg = new RegExp(pattern)
  let parse = name.match(reg)
  name_html = ''
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
    window.localStorage.setItem('name-html-' + a.dataset.name, name_html)
    a.innerHTML = '[' + name_html + ']'
  }
  else {
    window.localStorage.setItem('name-plain-' + a.dataset.name, '#')
    a.textContent = '[' + a.dataset.name + ']'
  }
}

TCENames.setup = function() {
  var codes = new Map()
  this.ncodes = codes

  if (!window.localStorage.getItem('version1')) {
    window.localStorage.setItem('version1', '#')
    window.localStorage.removeItem('name-html-^.Chucky<3')
    console.log('version1 done');
  }

  var tce_types = new Map()
  this.tce_types_map = tce_types

  tce_types.set('2', 'CTF')
  tce_types.set('5', 'Obj')
  tce_types.set('7', 'BC')

  var types = new Map()
  this.types_map = types

  types.set('4', 'CMP')
  types.set('2', 'Obj')
  types.set('5', 'LMS')

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
  
  codes.set('.', 'c-w')
}

TCENames.setup()
