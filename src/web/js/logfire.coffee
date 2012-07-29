
$(document).ready ->

  socket = new WebSocket("ws://#{window.location.host}/rt");
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


  $('#refresh').click ->
    components = $('#components').val() or ''
    levels = $('#levels').val() or ''

    $.ajax(
      '/'
      {
        type : 'POST'
        data : {
          components : String(components)
          levels : String(levels)
          limit : 25
          offset : 0
        }
        success : (response) ->
          $('table').empty()
          if response.result is 'SUCCESS'
            for row in response.rows
              tr = $('<tr></tr>')
                .append($('<td></td>').text(row['tstamp']))
                .append($('<td></td>').text(row['lvl']))
                .append($('<td></td>').text(row['comp']))

              msg = row['msg'].replace('\n','<br/>')
              tr.append($('<td></td>').html(msg))
              $('table').append(tr)

        error : (jqXhr, txtStatus, errThrown) ->
      }
    )


