#!/usr/bin/osascript -l JavaScript

ObjC.import('stdlib')

Array.prototype.contains = function(val) {
  for (var i; i < this.length; i++) {
    if (this[i] === val)
      return true
  }
  return false
}

app = Application('Viscosity')
help = `viscosity.js <command> [<name>]

Usage:
    viscosity.js (connect|disconnect) <name>
    viscosity.js list
    viscosity.js -h

Options:
    -h, --help    Show this message and quit
`

// Return true if specified VPN is connected.
function isActive(name) {
  for (var i=0; i < app.connections.length; i++) {
    var conn = app.connections[i]
    if (conn.name() == name) {
      return conn.state() == 'Connected'
    }
  }
  return false
}


// Show CLI help.
function showHelp(errMsg) {
  var status = 0
  if (errMsg) {
    console.log(`error: ${errMsg}`)
    status = 1
  }
  console.log(help)
  $.exit(status)
}


// Parse command-line flags.
function parseArgs(argv) {
  if (argv.length == 0 || argv.contains('-h') || argv.contains('--help')) {
    showHelp()
  }

  var command = argv[0],
      opts = {command: command, name: ''}

  if (command === 'list') {
    return opts
  }

  if (command === 'connect' || command === 'disconnect') {
    if (argv.length < 2) {
      showHelp('no VPN name specified')
    }
    opts.name = argv[1]
    return opts
  }

  showHelp(`unknown command: ${command}`)
}


// Connect to specified VPN.
function connect(name) {
  if (isActive(name)) {
    console.log(`VPN ${name} is already connected`)
    return
  }
  app.connect(name)
}


// Disconnect specified VPN.
function disconnect(name) {
  if (!isActive(name)) {
    console.log(`VPN ${name} is not connected`)
    return
  }
  app.disconnect(name)
}

// Return JSON mapping of connections to connected state.
function list() {
  var connections = {}

  for (var i=0; i < app.connections.length; i++) {
    var conn = app.connections[i]
    connections[conn.name()] = conn.state() == 'Connected'
  }

  return JSON.stringify(connections)
}


function run(argv) {
  opts = parseArgs(argv)
  switch (opts.command) {
    case 'connect':
      return connect(opts.name)
    case 'disconnect':
      return disconnect(opts.name)
    case 'list':
      return list()
  }
}