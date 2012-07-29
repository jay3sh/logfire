(function() {
  var refresh,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  refresh = function(components, levels) {
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
  };

  $(document).ready(function() {
    var levels, socket;
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
    levels = $('optgroup[label=Levels] option').map(function(i, el) {
      return $(el).text();
    });
    return $('#filter').chosen().change(function(ev) {
      var comp, filter, lvl, _i, _len, _ref;
      comp = [];
      lvl = [];
      _ref = $(this).val();
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        filter = _ref[_i];
        if (__indexOf.call(levels, filter) >= 0) {
          lvl.push(filter);
        } else {
          comp.push(filter);
        }
      }
      return refresh(comp.length > 0 ? String(comp) : '', lvl.length > 0 ? String(lvl) : '');
    });
  });

}).call(this);
