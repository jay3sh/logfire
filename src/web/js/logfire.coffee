
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

msgcolors = ['#999','#000','#520202','#A70505','#F00']

onetimeQuery = (components, levels, offset) ->
  $('table').empty()
  msg = {
    cmd : 'onetime'
    comp : String(components)
    lvl : String(levels)
    limit : 25
    offset : offset or 0
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
      .append($('<td></td>').text(tstamp).addClass('tstamp'))
      .append($('<td></td>').text(row['comp']).addClass('comp'))

    longmsg = shortmsg = row['msg']
    if row['msg'].indexOf('\n') >= 0
      msg = shortmsg = row['msg'].substring(0,row['msg'].indexOf('\n'))
      longmsg = row['msg'].replace(/\n/g,'<br>')
    else
      msg = row['msg']
    tr.append($('<td></td>').html(msg).addClass('msg'))

    tr.data('longmsg', longmsg)
    tr.data('shortmsg', shortmsg)
    tr.click ->
      elem = $(@).find('.msg')
      if $(@).data('longmsg') isnt $(@).data('shortmsg')
        if elem.data('isExpanded')
          elem.empty().html($(@).data('shortmsg')).data('isExpanded', false)
        else
          elem.empty().html($(@).data('longmsg')).data('isExpanded', true)

    if longmsg isnt shortmsg
      tr.find('.msg').css('cursor','pointer')

    tr.css('color',msgcolors[parseInt(row['lvl'],10)])

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
    $(document).data('page',0)

  $('#next').click () ->
    filters = getFilters()
    page = $(document).data('page') || 0
    console.log page
    onetimeQuery(
      if filters.comp.length > 0 then String(filters.comp) else '',
      if filters.lvl.length > 0 then String(filters.lvl) else '',
      (page+1) * 25
    )
    $(document).data('page',page+1)

  $('#prev').click () ->
    filters = getFilters()
    page = $(document).data('page')
    onetimeQuery(
      if filters.comp.length > 0 then String(filters.comp) else '',
      if filters.lvl.length > 0 then String(filters.lvl) else '',
      Math.max(page-1,0) * 25
    )
    $(document).data('page',Math.max(0,page-1))
    
window.onbeforeunload = ->
  if window.rtsocket then window.rtsocket.close()
