import logging
import selectors
import asyncio

_LOGGER = logging.getLogger(__name__)

# TODO: Auto-Restart when connection closes


class HRVManager:
    sel = selectors.DefaultSelector()

    my_mac = "12-34-56-78-12-34"
    hrv_mac = "D2-95-00-00-00-9E"

    message_handshake = f":DLF||{my_mac};"
    message_handshake_ack = f":DLF||{my_mac}|PS;"
    message_register_hrv = f":_CX|{hrv_mac}|0;"
    message_register_hrv_ack = f":_CX|{hrv_mac}|0|PS;"  # FA - response if HRV not found
    message_get_fan_speed = f":DAT|{hrv_mac}|{my_mac}|<stx>L76<etx>;"
    message_get_fan_speed_ack = f":DAT|{hrv_mac}|{my_mac}|PS"

    # Set fan speed
    fan_speed1 = f"F1{ '%03d' % (70 ^ 49)}"
    fan_speed2 = f"F2{ '%03d' % (70 ^ 50)}"
    fan_speed3 = f"F3{ '%03d' % (70 ^ 51)}"
    fan_speed4 = f"F4{ '%03d' % (70 ^ 52)}"
    message_set_fan_1 = (
        f":DAT|D2-95-00-00-00-9E|12-34-56-78-12-34|<stx>{ fan_speed1 }<etx>;"
    )
    message_set_fan_2 = (
        f":DAT|D2-95-00-00-00-9E|12-34-56-78-12-34|<stx>{ fan_speed2 }<etx>;"
    )
    message_set_fan_3 = (
        f":DAT|D2-95-00-00-00-9E|12-34-56-78-12-34|<stx>{ fan_speed3 }<etx>;"
    )
    message_set_fan_4 = (
        f":DAT|D2-95-00-00-00-9E|12-34-56-78-12-34|<stx>{ fan_speed4 }<etx>;"
    )

    update_callbacks = []

    def __init__(self):
        self.messages = []
        self.messages = [self.message_handshake]
        self.speed = 0

    def split_into_bits(self, number):
        # Use bin() to get the binary representation and remove the '0b' prefix
        binary_representation = bin(number)[2:]

        # Pad with leading zeros to ensure a consistent length
        padded_binary = binary_representation.zfill(8)  # Assuming 8 bits for simplicity

        # Convert the binary string to a list of integers
        bits = [int(bit) for bit in padded_binary]

        return bits

    def set_speed(self, speed):
        if speed == 1:
            self.messages.append(self.message_set_fan_1)
        if speed == 2:
            self.messages.append(self.message_set_fan_2)
        if speed == 3:
            self.messages.append(self.message_set_fan_3)
        if speed == 4:
            self.messages.append(self.message_set_fan_4)

        self.messages.append(self.message_get_fan_speed)

    async def receive_messages(self, reader):
        while True:
            data = await reader.readuntil(b";")

            # TODO: Reconnect on disconnect
            # Traceback (most recent call last):
            # File "/config/custom_components/minimal_integration/HRVManager.py", line 65, in receive_messages
            #     data = await reader.readuntil(b';')
            #         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            # File "/usr/local/lib/python3.11/asyncio/streams.py", line 637, in readuntil
            #     raise exceptions.IncompleteReadError(chunk, None)
            # asyncio.exceptions.IncompleteReadError: 0 bytes read on a total of undefined expected bytes

            if not data:
                break

            string = data.decode()
            _LOGGER.debug(f"<<< {string}")
            if string == self.message_handshake_ack:
                self.messages.append(self.message_register_hrv)
            elif string == self.message_register_hrv_ack:
                self.messages.append(self.message_get_fan_speed)
            elif string.startswith(self.message_get_fan_speed_ack):
                try:
                    payload = string.removeprefix(
                        self.message_get_fan_speed_ack + "|"
                    ).removesuffix(";")
                    if payload == "<stx>F<ack><etx>":
                        # Setting speed confirmed, reloading config
                        self.messages.append(self.message_get_fan_speed)
                    else:
                        payload = payload.removeprefix("<stx>L").removesuffix("<etx>")
                        speed_hex = payload[3:5]
                        bits = self.split_into_bits(int(speed_hex, 16))

                        new_speed = 0
                        if bits[0]:
                            new_speed = 1
                        elif bits[1]:
                            new_speed = 2
                        elif bits[2]:
                            new_speed = 3
                        elif bits[3]:
                            new_speed = 4

                        if new_speed != self.speed:
                            self.speed = new_speed
                            for callback in self.update_callbacks:
                                callback()

                        _LOGGER.debug(f"Speed: {self.speed}")

                        frost = (
                            "Frost protection ON" if bits[4] else "Frost protection OFF"
                        )
                        _LOGGER.debug(frost)

                        loop = asyncio.get_event_loop()

                        async def schedule_job():
                            await asyncio.sleep(5)
                            self.messages.append(self.message_get_fan_speed)

                        loop.create_task(schedule_job())
                except Exception as e:
                    _LOGGER.error(e)

    async def send_messages(self, writer):
        while True:
            try:
                message = self.messages.pop()
                message = message
                _LOGGER.debug(f">>> {message}")
                writer.write(message.encode())
                await writer.drain()
            except IndexError:
                await asyncio.sleep(0.1)  # Avoid blocking the event loop

    async def main(self):
        # TODO: Need to confirm connection can be established and return True/False

        reader, writer = await asyncio.open_connection("app.manageiaq.com", 6275)

        asyncio.get_event_loop().create_task(self.receive_messages(reader))
        asyncio.get_event_loop().create_task(self.send_messages(writer))

        _LOGGER.debug("HRV RUNNING")

    async def start(self):
        await self.main()
