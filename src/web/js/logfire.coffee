
Date.prototype.getRelativeTimestamp = ->
  tzoffset = @getTimezoneOffset() * 60 * 1000
  currDate = new Date()
  relativeDate = new Date(@getTime() - tzoffset)
  delta = Math.round((currDate - relativeDate)/1000)
  rtstamp = ''

  if delta < 60
    rtstamp = delta + ' seconds ago'
  else if delta < (60*60)
    rtstamp = Math.round(delta/60) + ' minutes ago'
  else if delta < (60*60*24)
    rtstamp = Math.round(delta/(60*60)) + ' hours ago'
  else if delta < (60*60*24*31)
    rtstamp = Math.round(delta/(60*60*24)) + ' days ago'
  else
    rtstamp = relativeDate.toDateString()
  return rtstamp

onetimeQuery = (components, levels) ->
  $('table').empty()
  msg = {
    cmd : 'onetime'
    comp : String(components)
    lvl : String(levels)
    limit : 25
    offset : 0
  }
  msg = JSON.stringify(msg)
  rtsocket.send(msg)

startRealTimeTailing = (components, levels) ->
  $('table').empty()
  msg = {
    cmd : 'startRT'
    comp : String(components)
    lvl : String(levels)
    limit : 25
    offset : 0
  }
  msg = JSON.stringify(msg)
  rtsocket.send(msg)

stopRealTimeTailing = (components, levels) ->
  msg = {
    cmd : 'stopRT'
  }
  msg = JSON.stringify(msg)
  rtsocket.send(msg)

getFilters = () ->
  comp = []
  lvl = []
  filters = $('#filter').val()
  if filters
    for filter in filters
      if filter in levels
        lvl.push(filter)
      else
        comp.push(filter)
  return { comp : comp, lvl : lvl }

rtChoice = false
levels = null

$(document).ready ->

  socket = new WebSocket("ws://#{window.location.host}/rt")
  socket.onopen = (ev) ->
  socket.onclose = (ev) ->
  socket.onmessage = (ev) ->
    row = JSON.parse(ev.data)
    tstamp = new Date(Date.parse(row['tstamp'])).getRelativeTimestamp()
    tr = $('<tr></tr>')
      .append($('<td></td>').text(tstamp))
      .append($('<td></td>').text(row['lvl']))
      .append($('<td></td>').text(row['comp']))

    longmsg = shortmsg = row['msg']
    if row['msg'].indexOf('\n') >= 0
      msg = shortmsg = row['msg'].substring(0,row['msg'].indexOf('\n'))
      longmsg = row['msg'].replace(/\n/g,'<br/>')
    else
      msg = row['msg']
    tr.append($('<td></td>').html(msg))

    tr.data('longmsg', longmsg)
    tr.data('shortmsg', shortmsg)
    tr.mouseenter ->
      if $(@).data('longmsg') isnt $(@).data('shortmsg')
        $(@).find('td:last').empty().html($(@).data('longmsg'))
    tr.mouseleave ->
      if $(@).data('longmsg') isnt $(@).data('shortmsg')
        $(@).find('td:last').empty().html($(@).data('shortmsg'))

    $('table').prepend(tr)
  socket.onerror = (ev) ->

  window.rtsocket = socket

  levels = $('optgroup[label=Levels] option').map (i,el)->$(el).text()

  $('#rtchoice').iButton({
    labelOn : 'Auto'
    labelOff : 'Manual'
    click : (newChoice) ->
      if newChoice is not window.rtChoice
        filters = getFilters()
        if newChoice
          startRealTimeTailing(
            if filters.comp.length > 0 then String(filters.comp) else '',
            if filters.lvl.length > 0 then String(filters.lvl) else '',
          )
          $('#refresh').attr('disabled',true)
        else
          stopRealTimeTailing()
          onetimeQuery(
            if filters.comp.length > 0 then String(filters.comp) else '',
            if filters.lvl.length > 0 then String(filters.lvl) else '',
          )
          $('#refresh').attr('disabled',false)
      window.rtChoice = newChoice
        
  })
  $('#rtchoice').iButton('toggle', false)

  $('#filter').chosen().change (ev) ->

    filters = getFilters()

    if window.rtChoice
      startRealTimeTailing(
        if filters.comp.length > 0 then String(filters.comp) else '',
        if filters.lvl.length > 0 then String(filters.lvl) else '',
      )
    else
      onetimeQuery(
        if filters.comp.length > 0 then String(filters.comp) else '',
        if filters.lvl.length > 0 then String(filters.lvl) else '',
      )

  $('#refresh').click () ->
    filters = getFilters()
    onetimeQuery(
      if filters.comp.length > 0 then String(filters.comp) else '',
      if filters.lvl.length > 0 then String(filters.lvl) else '',
    )
    
window.onbeforeunload = ->
  if window.rtsocket then window.rtsocket.close()
