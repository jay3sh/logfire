(function() {

  $(document).ready(function() {
    var socket;
    socket = new WebSocket("ws://" + window.location.host + "/rt");
    socket.onopen = function(ev) {};
    socket.onclose = function(ev) {};
    socket.onmessage = function(ev) {
      var msg, row, tr;
      row = JSON.parse(ev.data);
      tr = $('<tr></tr>').append($('<td></td>').text(row['tstamp'])).append($('<td></td>').text(row['lvl'])).append($('<td></td>').text(row['comp']));
      msg = row['msg'].replace('\n', '<br/>');
      tr.append($('<td></td>').html(msg));
      return $('table').prepend(tr);
    };
    socket.onerror = function(ev) {};
    $('#filter').chosen();
    return $('#refresh').click(function() {
      var components, levels;
      components = $('#components').val() || '';
      levels = $('#levels').val() || '';
      return $.ajax('/', {
        type: 'POST',
        data: {
          components: String(components),
          levels: String(levels),
          limit: 25,
          offset: 0
        },
        success: function(response) {
          var msg, row, tr, _i, _len, _ref, _results;
          $('table').empty();
          if (response.result === 'SUCCESS') {
            _ref = response.rows;
            _results = [];
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              row = _ref[_i];
              tr = $('<tr></tr>').append($('<td></td>').text(row['tstamp'])).append($('<td></td>').text(row['lvl'])).append($('<td></td>').text(row['comp']));
              msg = row['msg'].replace('\n', '<br/>');
              tr.append($('<td></td>').html(msg));
              _results.push($('table').append(tr));
            }
            return _results;
          }
        },
        error: function(jqXhr, txtStatus, errThrown) {}
      });
    });
  });

}).call(this);
