

refresh = (components, levels) ->
  $('table').empty()
  msg = {
    cmd : 'refresh'
    comp : String(components)
    lvl : String(levels)
    limit : 25
    offset : 0
  }
  msg = JSON.stringify(msg)
  rtsocket.send(msg)

$(document).ready ->

  socket = new WebSocket("ws://#{window.location.host}/rt")
  socket.onopen = (ev) ->
  socket.onclose = (ev) ->
  socket.onmessage = (ev) ->
    row = JSON.parse(ev.data)
    tr = $('<tr></tr>')
      .append($('<td></td>').text(row['tstamp']))
      .append($('<td></td>').text(row['lvl']))
      .append($('<td></td>').text(row['comp']))
    msg = row['msg'].replace('\n','<br/>')
    tr.append($('<td></td>').html(msg))
    $('table').prepend(tr)
  socket.onerror = (ev) ->

  window.rtsocket = socket

  levels = $('optgroup[label=Levels] option').map (i,el)->$(el).text()

  $('#rtchoice').iButton({
    labelOn : 'RealTime',
    labelOff : 'Manual'
  })

  $('#filter').chosen().change (ev) ->
    comp = []
    lvl = []
    filters = $(@).val()
    if filters
      for filter in filters
        if filter in levels
          lvl.push(filter)
        else
          comp.push(filter)

    refresh(
      if comp.length > 0 then String(comp) else '',
      if lvl.length > 0 then String(lvl) else '',
    )

window.onbeforeunload = ->
  if window.rtsocket then window.rtsocket.close()
