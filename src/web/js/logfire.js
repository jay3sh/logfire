(function() {
  var getFilters, levels, msgcolors, onetimeQuery, rtChoice, startRealTimeTailing, stopRealTimeTailing,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  Date.prototype.getRelativeTimestamp = function() {
    var currDate, delta, relativeDate, rtstamp, tzoffset;
    tzoffset = this.getTimezoneOffset() * 60 * 1000;
    currDate = new Date();
    relativeDate = new Date(this.getTime() - tzoffset);
    delta = Math.round((currDate - relativeDate) / 1000);
    rtstamp = '';
    if (delta < 60) {
      rtstamp = delta + ' seconds ago';
    } else if (delta < (60 * 60)) {
      rtstamp = Math.round(delta / 60) + ' minutes ago';
    } else if (delta < (60 * 60 * 24)) {
      rtstamp = Math.round(delta / (60 * 60)) + ' hours ago';
    } else if (delta < (60 * 60 * 24 * 31)) {
      rtstamp = Math.round(delta / (60 * 60 * 24)) + ' days ago';
    } else {
      rtstamp = relativeDate.toDateString();
    }
    return rtstamp;
  };

  msgcolors = ['#999', '#000', '#520202', '#A70505', '#F00'];

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
      var longmsg, msg, row, shortmsg, tr, tstamp;
      row = JSON.parse(ev.data);
      tstamp = new Date(Date.parse(row['tstamp'])).getRelativeTimestamp();
      tr = $('<tr></tr>').append($('<td></td>').text(tstamp).addClass('tstamp')).append($('<td></td>').text(row['comp']).addClass('comp'));
      longmsg = shortmsg = row['msg'];
      if (row['msg'].indexOf('\n') >= 0) {
        msg = shortmsg = row['msg'].substring(0, row['msg'].indexOf('\n'));
        longmsg = row['msg'].replace(/\n/g, '<br>');
      } else {
        msg = row['msg'];
      }
      tr.append($('<td></td>').html(msg).addClass('msg'));
      tr.data('longmsg', longmsg);
      tr.data('shortmsg', shortmsg);
      tr.click(function() {
        var elem;
        elem = $(this).find('.msg');
        if ($(this).data('longmsg') !== $(this).data('shortmsg')) {
          if (elem.html() === $(this).data('longmsg')) {
            return $(this).find('.msg').empty().html($(this).data('shortmsg'));
          } else {
            return $(this).find('.msg').empty().html($(this).data('longmsg'));
          }
        }
      });
      if (longmsg !== shortmsg) {
        tr.find('.msg').css('cursor', 'pointer');
      }
      tr.css('color', msgcolors[parseInt(row['lvl'], 10)]);
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
        if (newChoice === !window.rtChoice) {
          filters = getFilters();
          if (newChoice) {
            startRealTimeTailing(filters.comp.length > 0 ? String(filters.comp) : '', filters.lvl.length > 0 ? String(filters.lvl) : '');
            $('#refresh').attr('disabled', true);
          } else {
            stopRealTimeTailing();
            onetimeQuery(filters.comp.length > 0 ? String(filters.comp) : '', filters.lvl.length > 0 ? String(filters.lvl) : '');
            $('#refresh').attr('disabled', false);
          }
        }
        return window.rtChoice = newChoice;
      }
    });
    $('#rtchoice').iButton('toggle', false);
    $('#filter').chosen().change(function(ev) {
      var filters;
      filters = getFilters();
      if (window.rtChoice) {
        return startRealTimeTailing(filters.comp.length > 0 ? String(filters.comp) : '', filters.lvl.length > 0 ? String(filters.lvl) : '');
      } else {
        return onetimeQuery(filters.comp.length > 0 ? String(filters.comp) : '', filters.lvl.length > 0 ? String(filters.lvl) : '');
      }
    });
    return $('#refresh').click(function() {
      var filters;
      filters = getFilters();
      return onetimeQuery(filters.comp.length > 0 ? String(filters.comp) : '', filters.lvl.length > 0 ? String(filters.lvl) : '');
    });
  });

  window.onbeforeunload = function() {
    if (window.rtsocket) {
      return window.rtsocket.close();
    }
  };

}).call(this);
