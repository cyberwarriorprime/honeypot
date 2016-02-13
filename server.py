#!/usr/bin/env python2
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import socket, SocketServer, struct, subprocess, sys, time, traceback

from h_telnet import handle_telnet
from h_http import handle_http

def handle_default(socket, dstport):
	#socket.send("What!?\n")
	time.sleep(6)
	socket.close()

handlers = {
	23: handle_telnet,
	80: handle_http
}

class SingleTCPHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		# self.request is the socket
		srcaddr, srcport = self.request.getpeername()
		dstaddr, dstport = self.getoriginaldest()
		if dstaddr == '192.168.1.123':
			print("Intruder {}:{} connected to fake port {}".format(srcaddr, srcport, dstport))
			handler = handlers.get(dstport, handle_default)
			try:
				handler(self.request, dstport)
			except Exception as err:
				print(traceback.format_exc())

			self.request.close()
		else:
			print("Unexpected connection from {}:{} to {}:{}. Closing it.".format(srcaddr, srcport, dstaddr, dstport))
			self.request.send("Get out!\n")
			self.request.close()

	def getoriginaldest(self):
		SO_ORIGINAL_DST = 80
		odestdata = self.request.getsockopt(socket.SOL_IP, SO_ORIGINAL_DST, 16)
		_, port, a1, a2, a3, a4 = struct.unpack("!HHBBBBxxxxxxxx", odestdata)
		address = "%d.%d.%d.%d" % (a1, a2, a3, a4)
		return address, port

class SimpleServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	daemon_threads = True
	allow_reuse_address = True

	def __init__(self, server_address, RequestHandlerClass):
		SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)

server = SimpleServer(('0.0.0.0', 1211), SingleTCPHandler)
try:
	server.serve_forever()
except KeyboardInterrupt:
	sys.exit(0)
