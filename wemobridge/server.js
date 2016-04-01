//
// Example URL: http://rackpi6.local:8081/off?id=B4750E1B957858BF
//

var http = require('http');
var request = require('request');
var util = require('util');

var payload = '<?xml version="1.0" encoding="utf-8"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SetDeviceStatus xmlns:u="urn:Belkin:service:bridge:1"><DeviceStatusList>&lt;?xml version="1.0" encoding="UTF-8"?&gt;&lt;DeviceStatus&gt;&lt;IsGroupAction&gt;NO&lt;/IsGroupAction&gt;&lt;DeviceID available="YES"&gt;%s&lt;/DeviceID&gt;&lt;CapabilityID&gt;10006,10008&lt;/CapabilityID&gt;&lt;CapabilityValue&gt;%d,%d&lt;/CapabilityValue&gt;&lt;/DeviceStatus&gt;</DeviceStatusList></u:SetDeviceStatus></s:Body></s:Envelope>';

http.createServer(function(req, res) {
  var url = require('url').parse(req.url, true);

  var message = util.format('%s: %s action requested for %s', new Date(), url.pathname, url.query.id);
  if (url.query.intensity) {
    message += util.format(' (intensity: %d)', url.query.intensity);
  }
  console.log(message);

  // state: 0=off, 1=on
  var state = 0;
  var intensity = 0;

  if (url.pathname === '/on') {
    // default to full brightness
    intensity = url.query.intensity ? url.query.intensity : 255;
    state = 1;
  }

  // send the request to the WeMo Link
  request({
    url: 'http://10.0.0.104:49153/upnp/control/bridge1',
    method: 'POST',
    headers: {
      'content-type': 'text/xml',
      'SOAPACTION': '"urn:Belkin:service:bridge:1#SetDeviceStatus"',
    },
    body: util.format(payload, url.query.id, state, intensity),
  }, function(error, response, body) {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end(body);
  });
}).listen(8081);
