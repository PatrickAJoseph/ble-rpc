
import ble_rpc
import asyncio
import sys
import time

RPC_RESPONSE_TIMEOUT = 1000

async def main():

    if len(sys.argv) != 2:

        print(f"Usage:\n python {sys.argv[0]} \"Device Name\"")

        return 1

    device_name = sys.argv[1]

    rpc = ble_rpc.RPC(device_name, 'rpc_data.yaml')

    rpc.disassemble_response_packet(b'\x00\x04\x00\x00\x00\xA1')
    print(rpc.get_rpc_response_parameter_value('ping_device_1', 'ping_count'))

'''

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
            print(f"---------------- Command {i + 1} / {number_of_commands} ----------------")

            start_time = time.perf_counter()

            try:

                response = await rpc.send_command(command,timeout=RPC_RESPONSE_TIMEOUT)

                end_time = time.perf_counter()

                response_time_ms = (end_time - start_time) * 1000.0

                response_times.append(response_time_ms)

                print(f"[RPC] Complete round-trip time: {response_time_ms:.3f} ms")

                print(f"[RPC] Response: {response.hex(' ')}")

            except asyncio.TimeoutError:

                print("[RPC] Command failed: no response received.")

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

'''


# ============================================================================
# Program entry
# ============================================================================

if __name__ == "__main__":

    try:
        exit_code = asyncio.run(main())

    except KeyboardInterrupt:
        exit_code = 1

    sys.exit(exit_code)