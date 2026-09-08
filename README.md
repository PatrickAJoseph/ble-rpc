# ble-rpc
Bluetooth remote procedure call.
This repository contains the implementation of bluetooth service consisting of three
characteristics: command, response and notification. The client sends commands over
the command characteristics. Once the server has completed processing the command,
the server sends out a BLE notification letting the client know that the response is
available. The server can let know of events occuring in it by sending out notifications
(not to be confused with BLE notifications).