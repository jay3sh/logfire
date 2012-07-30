(function() {
  var getFilters, levels, onetimeQuery, rtChoice, startRealTimeTailing, stopRealTimeTailing,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  onetimeQuery = function(components, levels) {
    var msg;
    $('table').empty();
    msg = {
      cmd: 'onetime',
      comp: String(components),
      lvl: String(levels),
      limit: 25,
      offset: 0
    };
    msg = JSON.stringify(msg);
    return rtsocket.send(msg);
  };

  startRealTimeTailing = function(components, levels) {
    var msg;
    $('table').empty();
    msg = {
      cmd: 'startRT',
      comp: String(components),
      lvl: String(levels),
      limit: 25,
      offset: 0
    };
    msg = JSON.stringify(msg);
    return rtsocket.send(msg);
  };

  stopRealTimeTailing = function(components, levels) {
    var msg;
    msg = {
      cmd: 'stopRT'
    };
    msg = JSON.stringify(msg);
    return rtsocket.send(msg);
  };

  getFilters = function() {
    var comp, filter, filters, lvl, _i, _len;
    comp = [];
    lvl = [];
    filters = $('#filter').val();
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
    return {
      comp: comp,
      lvl: lvl
    };
  };

  rtChoice = false;

  levels = null;

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
    window.rtsocket = socket;
    levels = $('optgroup[label=Levels] option').map(function(i, el) {
      return $(el).text();
    });
    $('#rtchoice').iButton({
      labelOn: 'Auto',
      labelOff: 'Manual',
      click: function(newChoice) {
        var filters;
        if (newChoice === !rtChoice) {
          if (newChoice) {
            filters = getFilters();
            startRealTimeTailing(filters.comp.length > 0 ? String(filters.comp) : '', filters.lvl.length > 0 ? String(filters.lvl) : '');
          } else {
            stopRealTimeTailing();
            onetimeQuery(filters.comp.length > 0 ? String(filters.comp) : '', filters.lvl.length > 0 ? String(filters.lvl) : '');
          }
        }
        return rtChoice = newChoice;
      }
    });
    $('#rtchoice').iButton('toggle', false);
    return $('#filter').chosen().change(function(ev) {
      var filters;
      filters = getFilters();
      if (window.rtChoice) {
        return startRealTimeTailing(filters.comp.length > 0 ? String(filters.comp) : '', filters.lvl.length > 0 ? String(filters.lvl) : '');
      } else {
        return onetimeQuery(filters.comp.length > 0 ? String(filters.comp) : '', filters.lvl.length > 0 ? String(filters.lvl) : '');
      }
    });
  });

  window.onbeforeunload = function() {
    if (window.rtsocket) {
      return window.rtsocket.close();
    }
  };

}).call(this);
