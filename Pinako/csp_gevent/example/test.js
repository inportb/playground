jsio('import net');
jsio('import net.interfaces');

// Set logger to debug mode
logger.setLevel(0);

var TestProtocol = Class(net.interfaces.Protocol, function(supr) {
	
	this.connectionMade = function() {
		logger.debug('Connection Made!');
	}
	
	this.dataReceived = function(data) {
		logger.debug('Data Received:', data);
	}
	
	this.send = function(data) {
		logger.debug('sending:', data);
		this.transport.write(data);
	}
	
})


exports.establishConnection = function(url) {
	var cspUrl = url || '/csp';
	var p = new TestProtocol();
	net.connect(p, 'csp', { url: cspUrl })
	return p;
}
