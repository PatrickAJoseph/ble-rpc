import asyncio
import sys
import time

from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice


# ============================================================================
# BLE UUIDs
# ============================================================================

RPC_COMMAND_UUID = "0000e001-0000-1000-8000-00805f9b34fb"
RPC_RESPONSE_UUID = "0000e002-0000-1000-8000-00805f9b34fb"
RPC_NOTIFICATION_UUID = "0000e003-0000-1000-8000-00805f9b34fb"


# ============================================================================
# RPC configuration
# ============================================================================

RPC_MAX_PAYLOAD_LENGTH = 200
RPC_MAX_PACKET_LENGTH = RPC_MAX_PAYLOAD_LENGTH + 2

RPC_RESPONSE_TIMEOUT = 2.0
BLE_CONNECT_TIMEOUT = 15.0


# ============================================================================
# RPC client
# ============================================================================

class RPC:
    def __init__(self, device_name: str):
        self.device_name = device_name

        self.ble_device: BLEDevice | None = None
        self.client: BleakClient | None = None

        self.command_uuid = RPC_COMMAND_UUID
        self.response_uuid = RPC_RESPONSE_UUID
        self.notification_uuid = RPC_NOTIFICATION_UUID

        # Future representing the response to the currently outstanding RPC.
        self.response_future: asyncio.Future[bytes] | None = None

        # Prevent multiple commands from using the same response Future.
        self.command_lock = asyncio.Lock()

        # Number of responses received.
        self.response_count = 0

        # Number of asynchronous notifications received.
        self.notification_count = 0

    # ------------------------------------------------------------------------
    # BLE notification handlers
    # ------------------------------------------------------------------------

    def response_handler(self, sender, data: bytearray):
        """
        Called when E002 generates a BLE notification.

        Expected packet format:

            Byte 0       : response ID
            Byte 1       : payload length
            Bytes 2..N   : payload
        """

        print("----------**************************--------------------")


        response = bytes(data)

        self.response_count += 1

        print(
            f"[E002] Response received: "
            f"{response.hex(' ')}"
        )

        # Basic packet validation.
        if len(response) < 2:
            print("[E002] ERROR: response packet too short")
            return

        response_id = response[0]
        payload_length = response[1]

        if payload_length != len(response) - 2:
            print(
                f"[E002] ERROR: length mismatch: "
                f"header={payload_length}, "
                f"actual={len(response) - 2}"
            )
            return

        payload = response[2:]

        print(
            f"[E002] ID=0x{response_id:02X}, "
            f"Length={payload_length}, "
            f"Payload={payload.hex(' ')}"
        )

        # Resolve the Future belonging to the command currently being waited on.
        if self.response_future is not None:

            if self.response_future.done():
                print("[E002] WARNING: response future already completed")
                return

            # Store the complete RPC response.
            self.response_future.set_result(response)

    def notification_handler(self, sender, data: bytearray):
        """
        Called for asynchronous E003 notifications.

        Expected packet format:

            Byte 0       : notification ID
            Byte 1       : payload length
            Bytes 2..N   : payload
        """

        notification = bytes(data)

        self.notification_count += 1

        print(
            f"[E003] Notification received: "
            f"{notification.hex(' ')}"
        )

        if len(notification) < 2:
            print("[E003] ERROR: notification packet too short")
            return

        notification_id = notification[0]
        payload_length = notification[1]

        if payload_length != len(notification) - 2:
            print(
                f"[E003] ERROR: length mismatch: "
                f"header={payload_length}, "
                f"actual={len(notification) - 2}"
            )
            return

        payload = notification[2:]

        print(
            f"[E003] ID=0x{notification_id:02X}, "
            f"Length={payload_length}, "
            f"Payload={payload.hex(' ')}"
        )

    # ------------------------------------------------------------------------
    # Device discovery
    # ------------------------------------------------------------------------

    async def get_device(self):
        print(f"Searching for device: {self.device_name}")

        devices = await BleakScanner.discover(
            timeout=10.0
        )

        for device in devices:

            print(
                f"Found device: "
                f"{device.name} | "
                f"{device.address}"
            )

            if device.name == self.device_name:

                self.ble_device = device

                print()
                print("Target device found !")
                print(
                    f"Device name: {device.name} | "
                    f"Address: {device.address}"
                )

                return

        raise IOError(
            f"Target device '{self.device_name}' not found"
        )

    # ------------------------------------------------------------------------
    # Connect
    # ------------------------------------------------------------------------

    async def connect(self):

        if self.ble_device is None:
            await self.get_device()

        print()
        print("Connecting with server ...")

        self.client = BleakClient(
            self.ble_device
        )

        try:
            await asyncio.wait_for(
                self.client.connect(),
                timeout=BLE_CONNECT_TIMEOUT
            )

        except Exception as exc:
            raise IOError(
                f"Unable to connect to BLE device: {exc}"
            ) from exc

        print(
            f"Connected with {self.ble_device.name} "
            f"at address {self.ble_device.address}"
        )

        # --------------------------------------------------------------------
        # Discover services
        # --------------------------------------------------------------------

        services = self.client.services

        print()
        print("BLE services/characteristics:")

        for service in services:

            print(
                f"\nService: {service.uuid}"
            )

            for characteristic in service.characteristics:

                print(
                    f"  Characteristic UUID: "
                    f"{characteristic.uuid}"
                )

                print(
                    f"  Description: "
                    f"{characteristic.description}"
                )

        # --------------------------------------------------------------------
        # Verify RPC characteristics
        # --------------------------------------------------------------------

        if not self._find_characteristic(RPC_COMMAND_UUID):
            raise IOError(
                f"RPC command characteristic not found: "
                f"{RPC_COMMAND_UUID}"
            )

        if not self._find_characteristic(RPC_RESPONSE_UUID):
            raise IOError(
                f"RPC response characteristic not found: "
                f"{RPC_RESPONSE_UUID}"
            )

        if not self._find_characteristic(RPC_NOTIFICATION_UUID):
            raise IOError(
                f"RPC notification characteristic not found: "
                f"{RPC_NOTIFICATION_UUID}"
            )

        print()
        print("RPC characteristics found:")
        print(f"  Command      : {self.command_uuid}")
        print(f"  Response     : {self.response_uuid}")
        print(f"  Notification : {self.notification_uuid}")

        # --------------------------------------------------------------------
        # Enable notifications
        # --------------------------------------------------------------------

        print()
        print("Enabling RPC response notifications...")

        await self.client.start_notify(
            self.response_uuid,
            self.response_handler
        )

        print("RPC response notifications enabled.")

        print("Enabling RPC asynchronous notifications...")

        await self.client.start_notify(
            self.notification_uuid,
            self.notification_handler
        )

        print("RPC asynchronous notifications enabled.")

    # ------------------------------------------------------------------------
    # Characteristic lookup
    # ------------------------------------------------------------------------

    def _find_characteristic(self, uuid: str) -> bool:

        if self.client is None:
            return False

        target_uuid = uuid.lower()

        for service in self.client.services:

            for characteristic in service.characteristics:

                if characteristic.uuid.lower() == target_uuid:
                    return True

        return False

    # ------------------------------------------------------------------------
    # Send RPC command and wait for response
    # ------------------------------------------------------------------------

    async def send_command(
        self,
        command: bytes,
        timeout: float = RPC_RESPONSE_TIMEOUT
    ) -> bytes:

        if self.client is None or not self.client.is_connected:
            raise IOError("BLE client is not connected")

        if len(command) < 2:
            raise ValueError(
                "RPC command must contain ID and length"
            )

        if len(command) > RPC_MAX_PACKET_LENGTH:
            raise ValueError(
                f"RPC command too large: "
                f"{len(command)} bytes"
            )

        command_id = command[0]
        command_length = command[1]

        actual_payload_length = len(command) - 2

        if command_length != actual_payload_length:
            raise ValueError(
                f"RPC command length mismatch: "
                f"header={command_length}, "
                f"actual={actual_payload_length}"
            )

        async with self.command_lock:

            loop = asyncio.get_running_loop()

            # IMPORTANT:
            #
            # Create the Future BEFORE sending the command.
            #
            # The MCU could respond very quickly, so the response
            # notification could theoretically arrive immediately after
            # write_gatt_char() starts.
            self.response_future = loop.create_future()

            print()
            print(
                f"[RPC] Sending command "
                f"ID=0x{command_id:02X}, "
                f"Length={command_length}, "
                f"Data={command.hex(' ')}"
            )

            start_time = time.perf_counter()

            try:

                # response=True means wait for the ATT write response.
                await self.client.write_gatt_char(
                    self.command_uuid,
                    command,
                    response=True
                )

                # Now wait for the actual E002 notification.
                response = await asyncio.wait_for(
                    asyncio.shield(self.response_future),
                    timeout=timeout
                )

                end_time = time.perf_counter()

                response_time_ms = (
                    end_time - start_time
                ) * 1000.0

                print(
                    f"[RPC] Response time: "
                    f"{response_time_ms:.3f} ms"
                )

                return response

            except asyncio.TimeoutError:

                end_time = time.perf_counter()

                elapsed_ms = (
                    end_time - start_time
                ) * 1000.0

                print(
                    f"[RPC] ERROR: response timeout "
                    f"after {elapsed_ms:.3f} ms"
                )

                raise

            finally:
                self.response_future = None

    # ------------------------------------------------------------------------
    # Disconnect
    # ------------------------------------------------------------------------

    async def disconnect(self):

        if self.client is None:
            return

        try:

            if self.client.is_connected:

                print()
                print(
                    "Stopping RPC response notifications..."
                )

                try:
                    await self.client.stop_notify(
                        self.response_uuid
                    )
                except Exception as exc:
                    print(
                        f"Warning while stopping response "
                        f"notifications: {exc}"
                    )

                print(
                    "Stopping RPC asynchronous notifications..."
                )

                try:
                    await self.client.stop_notify(
                        self.notification_uuid
                    )
                except Exception as exc:
                    print(
                        f"Warning while stopping asynchronous "
                        f"notifications: {exc}"
                    )

                print("Disconnecting...")

                await self.client.disconnect()

        finally:

            self.client = None

            print("Disconnected.")


# ============================================================================
# Main test
# ============================================================================

async def main():

    if len(sys.argv) != 2:

        print(
            f"Usage:\n"
            f"    python {sys.argv[0]} \"Device Name\""
        )

        return 1

    device_name = sys.argv[1]

    rpc = RPC(device_name)

    try:

        # ================================================================
        # Everything happens inside ONE asyncio event loop.
        # ================================================================

        await rpc.connect()

        print()
        print("=" * 70)
        print("Starting RPC test")
        print("=" * 70)

        # ----------------------------------------------------------------
        # Test command
        #
        # Packet:
        #
        #   00 = command ID
        #   01 = payload length
        #   01 = payload
        #
        # ----------------------------------------------------------------

        command = bytes([
            0x00,
            0x01,
            0x01
        ])

        number_of_commands = 10

        response_times = []

        for i in range(number_of_commands):

            print()
            print(
                f"---------------- Command {i + 1}/"
                f"{number_of_commands} ----------------"
            )

            start_time = time.perf_counter()

            try:

                response = await rpc.send_command(
                    command,
                    timeout=RPC_RESPONSE_TIMEOUT
                )

                end_time = time.perf_counter()

                response_time_ms = (
                    end_time - start_time
                ) * 1000.0

                response_times.append(
                    response_time_ms
                )

                print(
                    f"[RPC] Complete round-trip time: "
                    f"{response_time_ms:.3f} ms"
                )

                print(
                    f"[RPC] Response: "
                    f"{response.hex(' ')}"
                )

            except asyncio.TimeoutError:

                print(
                    "[RPC] Command failed: "
                    "no response received."
                )

            # Use asyncio.sleep(), NOT time.sleep().
            #
            # time.sleep() blocks the asyncio event loop.
            await asyncio.sleep(1.0)

        # ----------------------------------------------------------------
        # Statistics
        # ----------------------------------------------------------------

        print()
        print("=" * 70)
        print("RPC test complete")
        print("=" * 70)

        if response_times:

            minimum = min(response_times)
            maximum = max(response_times)
            average = sum(response_times) / len(response_times)

            print(
                f"Responses received : "
                f"{len(response_times)}/{number_of_commands}"
            )

            print(
                f"Minimum            : "
                f"{minimum:.3f} ms"
            )

            print(
                f"Maximum            : "
                f"{maximum:.3f} ms"
            )

            print(
                f"Average            : "
                f"{average:.3f} ms"
            )

        print()
        print(
            f"E002 responses received: "
            f"{rpc.response_count}"
        )

        print(
            f"E003 notifications received: "
            f"{rpc.notification_count}"
        )

        return 0

    except KeyboardInterrupt:

        print()
        print("Interrupted by user.")

        return 1

    except Exception as exc:

        print()
        print(
            f"ERROR: {exc}"
        )

        return 1

    finally:

        await rpc.disconnect()


# ============================================================================
# Program entry
# ============================================================================

if __name__ == "__main__":

    try:
        exit_code = asyncio.run(main())

    except KeyboardInterrupt:
        exit_code = 1

    sys.exit(exit_code)