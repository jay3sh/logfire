(function() {
  var refresh,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  refresh = function(components, levels) {
    var msg;
    $('table').empty();
    msg = {
      cmd: 'refresh',
      comp: String(components),
      lvl: String(levels),
      limit: 25,
      offset: 0
    };
    msg = JSON.stringify(msg);
    return rtsocket.send(msg);
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
    window.rtsocket = socket;
    levels = $('optgroup[label=Levels] option').map(function(i, el) {
      return $(el).text();
    });
    return $('#filter').chosen().change(function(ev) {
      var comp, filter, filters, lvl, _i, _len;
      comp = [];
      lvl = [];
      filters = $(this).val();
      if (filters) {
        for (_i = 0, _len = filters.length; _i < _len; _i++) {
          filter = filters[_i];
          if (__indexOf.call(levels, filter) >= 0) {
            lvl.push(filter);
          } else {
            comp.push(filter);
          }
        }
      }
      return refresh(comp.length > 0 ? String(comp) : '', lvl.length > 0 ? String(lvl) : '');
    });
  });

  window.onbeforeunload = function() {
    if (window.rtsocket) {
      return window.rtsocket.close();
    }
  };

}).call(this);
