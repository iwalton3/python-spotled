from gattlib import GATTRequester
from threading import Event
from enum import Enum
import time
import os.path

class ByteWriter:
    """
    A class for writing bytes into binary blob by type sequentially.
    Also supports writing checksums for written data.
    """
    def __init__(self):
        self.content = bytearray()
        self.checksum_start_pos = 0
    
    def write_byte(self, value):
        self.content.append(value & 255)

    def write_short(self, value):
        self.content.append((value >> 8) & 255)
        self.content.append(value & 255)

    def write_int(self, value):
        self.content.append((value >> 24) & 255)
        self.content.append((value >> 16) & 255)
        self.content.append((value >> 8) & 255)
        self.content.append(value & 255)
    
    def write_bytes(self, value):
        self.content.extend(value)
    
    def start_checksum(self):
        self.checksum_start_pos = len(self.content)

    def write_checksum(self):
        value = 0
        for b in self.content[self.checksum_start_pos:]:
            value += 255 & b
        if value > 255:
            value = (~value) + 1
        self.content.append(value & 255)

    def to_bytes(self):
        return bytes(self.content)


class ByteReader:
    """
    A class for reading bytes out of a binary blob by type sequentially.
    """
    def __init__(self, content):
        self.content = content
        self.current_pos = 0
    
    def read_byte(self):
        value = self.content[self.current_pos]
        self.current_pos += 1
        return value

    def read_short(self):
        value = (self.content[self.current_pos] << 8) + self.content[self.current_pos + 1]
        self.current_pos += 2
        return value

    def read_int(self):
        value = (
            (self.content[self.current_pos] << 24) +
            (self.content[self.current_pos + 1] << 16) +
            (self.content[self.current_pos + 2] << 8) +
            self.content[self.current_pos + 3]
        )
        self.current_pos += 4
        return value
    
    def read_bytes(self, count):
        value = self.content[self.current_pos:self.current_pos+count]
        self.current_pos += count
        return value


def _find_service(req, uuid):
    return [x for x in req.discover_primary() if x['uuid'] == uuid][0]

def _find_handle(characteristic_info, uuid):
    return [x['value_handle'] for x in characteristic_info if x['uuid'] == uuid][0]

def _discover_handles(req):
    service_info = _find_service(req, '0000ff20-0000-1000-8000-00805f9b34fb');
    characteristic_info = req.discover_characteristics(service_info['start'], service_info['end'])
    cmd_handle = _find_handle(characteristic_info, '0000ff21-0000-1000-8000-00805f9b34fb')
    data_handle = _find_handle(characteristic_info, '0000ff22-0000-1000-8000-00805f9b34fb')

    return cmd_handle, data_handle


class SendingDataStartCommand:
    """
    Indicates to the device that it is about to be sent
    new command data.
    """
    def __init__(self, serial_no, command_type, command_length):
        self.serial_no = serial_no
        self.command_type = command_type
        self.command_length = command_length

    def serialize(self):
        d = ByteWriter()
        d.write_byte(10) # length
        d.write_byte(1) # SendingDataStartCommand
        d.write_short(self.serial_no)
        d.write_short(self.command_type)
        d.write_int(self.command_length)
        return d.to_bytes()

class SendingDataFinishCommand:
    """
    Indicates to the device that all of the command data
    has been sent off successfully.
    """
    def __init__(self, serial_no, command_type, command_length):
        self.serial_no = serial_no
        self.command_type = command_type
        self.command_length = command_length

    def serialize(self):
        d = ByteWriter()
        d.write_byte(10) # length
        d.write_byte(3) # SendingDataFinishCommand
        d.write_short(self.serial_no)
        d.write_short(self.command_type)
        d.write_int(self.command_length)
        return d.to_bytes()

class SendDataCommand:
    """
    The main command used to send data to the device
    including animations, text, and display settings.
    This wraps ByteWriter and handles checksums for you.
    """
    def __init__(self, content):
        self.serial_no = 1
        self.command_type = 32772
        self.content = content

    def serialize(self):
        d = ByteWriter()
        d.write_int(15) # length of header
        d.write_short(self.command_type)
        d.write_int(self.serial_no)
        d.write_int(len(self.content))
        d.write_checksum()
        d.write_bytes(self.content)
        return d.to_bytes()

class BrightnessData:
    """
    Specifies the brightness of the display
    from 0-100. Sent using a data command.
    """
    def __init__(self, brightness):
        self.brightness = brightness

    def serialize(self):
        d = ByteWriter()
        d.write_int(8) # length
        d.write_short(14) # type
        d.write_byte(self.brightness)
        d.write_checksum()
        return d.to_bytes()

class ScreenModeData:
    """
    Specifies if the screen should be flipped or
    mirrored. Sent using a data command.
    """
    def __init__(self, mode):
        self.mode = mode

    def serialize(self):
        d = ByteWriter()
        d.write_int(8) # length
        d.write_short(15)
        d.write_byte(self.mode)
        d.write_checksum()
        return d.to_bytes()

class ScreenMode(Enum):
    NORMAL = 0
    UPSIDE_DOWN = 1
    MIRROR = 2
    MIRROR_UPSIDE_DOWN = 3

class FontData:
    """
    Wraps a list of font character glyphs for text display.
    """
    def __init__(self, font_characters):
        self.font_characters = font_characters

    def serialize(self):
        d = ByteWriter()
        d.write_int(9) # length
        d.write_short(5) # type
        d.write_short(len(self.font_characters))
        d.write_checksum()
        for font_character in self.font_characters:
            d.write_bytes(font_character.serialize())
        return d.to_bytes()

class FontCharacterData:
    """
    Wraps a single character glyph. Must be sent before
    the glyph can be displayed in text mode.
    """
    def __init__(self, width, height, character, bitmap):
        self.width = width
        self.height = height
        self.character = character
        self.bitmap = bitmap

    def serialize(self):
        d = ByteWriter()
        d.write_int(len(self.bitmap) + 15) # length
        d.write_short(13) # type
        d.write_byte(1) # always 1?
        d.write_short(self.width)
        d.write_short(self.height)
        d.write_short(ord(self.character))
        d.write_byte(len(self.bitmap))
        d.write_bytes(self.bitmap)
        d.write_checksum()
        return d.to_bytes()

def gen_bitmap(*lines, min_len=0, true_char='1'):
    """
    Converts a "text" bitmap consisting of . and 1
    to a raw binary bitmap. min_len sets the minimum
    row length.
    """
    if min_len % 8 != 0:
        min_len += 8 - (min_len % 8)

    data = bytearray()
    for text in lines:
        if len(text) < min_len:
            text += '.' * (min_len - len(text))
        else:
            excess = len(text) % 8
            if excess != 0:
                text += '.' * (8 - excess)
        for i in range(0, len(text), 8):
            data.append(
                ((text[i] == true_char) << 7) |
                ((text[i+1] == true_char) << 6) |
                ((text[i+2] == true_char) << 5) |
                ((text[i+3] == true_char) << 4) |
                ((text[i+4] == true_char) << 3) |
                ((text[i+5] == true_char) << 2) |
                ((text[i+6] == true_char) << 1) |
                (text[i+7] == true_char)
            )
    return bytes(data)

class TimeData:
    """
    The amount of time in milliseconds to show each frame of
    an animation. Only used if there is no effect applied.
    """
    def __init__(self, time):
        self.time = time

    def serialize(self):
        d = ByteWriter()
        d.write_int(10) # length
        d.write_short(7) # type
        d.write_byte(0) # always zero?
        d.write_short(self.time)
        d.write_checksum()
        return d.to_bytes()

class SpeedData:
    """
    The speed of the animation. Used if effect is not none.
    """
    def __init__(self, speed):
        self.speed = speed

    def serialize(self):
        d = ByteWriter()
        d.write_int(8) # length
        d.write_short(9) # type
        d.write_byte(self.speed)
        d.write_checksum()
        return d.to_bytes()

class Effect(Enum):
    NONE = 0
    SCROLL_UP = 1
    SCROLL_DOWN = 2
    SCROLL_LEFT = 3
    SCROLL_RIGHT = 4
    STACK = 5
    EXPAND = 6
    LASER = 7

class Align(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2

class EffectData:
    """
    Indicates the display mode (static, scrolling, etc)
    for text/animations on the device.
    """
    def __init__(self, effect: Effect):
        self.effect = effect

    def serialize(self):
        d = ByteWriter()
        d.write_int(8) # length
        d.write_short(8) # type
        d.write_byte(self.effect.value)
        d.write_checksum()
        return d.to_bytes()

class FrameData:
    """
    A single display frame. Use gen_bitmap to generate one
    from text consisting of ./1 or convert the lines to
    bytes in order. Also supports specifying a color
    depth but I have no such devices to test this on.
    """
    def __init__(self, width, height, bitmap, depth=1):
        self.width = width
        self.height = height
        self.bitmap = bitmap
        self.depth = depth

    def serialize(self):
        d = ByteWriter()
        d.write_int(len(self.bitmap) + 12) # length
        d.write_short(96) # type
        d.write_short(self.width)
        d.write_short(self.height)
        d.write_byte(self.depth)
        d.write_bytes(self.bitmap)
        d.write_checksum()
        return d.to_bytes()

class AnimationData:
    """
    Wraps a series of frames (max 20) along with speed, time,
    and effect data. Time is per-frame time, but it is only
    used if no effects are used.
    """
    def __init__(self, frames, time, speed, effects: Effect):
        self.frames = frames
        self.time = time
        self.speed = speed
        self.effects = effects

    def serialize(self):
        d = ByteWriter()
        d.write_int(9) # length
        d.write_short(11) # type
        d.write_short(len(self.frames))
        d.write_checksum()
        for frame in self.frames:
            d.write_bytes(frame.serialize())
        d.write_bytes(TimeData(self.time).serialize())
        d.write_bytes(SpeedData(self.speed).serialize())
        d.write_bytes(EffectData(self.effects).serialize())
        return d.to_bytes()

class CharacterData:
    """
    A single unicode character value.
    """
    def __init__(self, char):
        self.char = char

    def serialize(self):
        d = ByteWriter()
        d.write_int(9) # length
        d.write_short(3) # type
        d.write_short(ord(self.char))
        d.write_checksum()
        return d.to_bytes()

class ColorData:
    """
    An RGB color value. Used for text.
    """
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def serialize(self):
        d = ByteWriter()
        d.write_int(10) # length
        d.write_short(2) # type
        d.write_byte(self.red)
        d.write_byte(self.green)
        d.write_byte(self.blue)
        d.write_checksum()
        return d.to_bytes()

class TextData:
    """
    This wraps a list of characters. The character glyphs
    must have been sent previously or the device will not
    be able to display them properly. It also sends colors
    and speed/effect data.
    """
    def __init__(self, text, speed, effects: Effect, colors=None):
        self.text = text
        self.colors = colors
        self.speed = speed
        self.effects = effects

    def serialize(self):
        d = ByteWriter()
        d.write_int(10) # length
        d.write_short(4) # type
        d.write_short(len(self.text))
        d.write_byte(1) # always 1?
        d.write_checksum()
        for i, character in enumerate(self.text):
            if self.colors is not None:
                d.write_bytes(self.colors[i].serialize())
            else:
                d.write_bytes(ColorData(255, 255, 255).serialize())
            d.write_bytes(CharacterData(character).serialize())
        d.write_bytes(SpeedData(self.speed).serialize())
        d.write_bytes(TimeData(0).serialize())
        d.write_bytes(EffectData(self.effects).serialize())
        return d.to_bytes()

class NumberBarData:
    """
    Graphs 16 values from 0-12 as a bar graph. Intended for
    displaying a music spectrum display.
    """
    def __init__(self, values):
        self.values = values

    def serialize(self):
        d = ByteWriter()
        d.write_int(len(self.values) * 2 + 9) # length
        d.write_short(10) # type
        d.write_short(len(self.values))
        for value in self.values:
            d.write_short(value)
        d.write_checksum()
        return d.to_bytes()

class GenericCommandResponse:
    """
    This is the generic response wrapper for commands
    that indicates the response type.
    """
    def __init__(self, data):
        d = ByteReader(data)
        d.read_bytes(3) # junk data?
        length = d.read_byte()
        self.command_type = d.read_byte()
        self.content = d.read_bytes(length - 2)

class SendingDataResponse:
    """
    This response is send from the device after you send it a request to
    send a data command.
    """
    def __init__(self, content):
        assert len(content) == 5
        d = ByteReader(content)
        self.serial_no = d.read_short()
        self.error_code = d.read_byte()
        self.command_type = d.read_short()

class ContinueSendingResponse:
    """
    This response is send from the device after it has finished processing
    the last 6 data commands and is ready for more data.
    """
    def __init__(self, content):
        assert len(content) == 8
        d = ByteReader(content)
        self.serial_no = d.read_short()
        self.command_type = d.read_short()
        self.continue_from = d.read_int()

def getCommandResponse(data):
    response = GenericCommandResponse(data)

    if (response.command_type == 2):
        return SendingDataResponse(response.content)

    if (response.command_type == 255):
        return ContinueSendingResponse(response.content)

    return response

def parse_yaff_font(fontfile):
    font = {}
    with open(fontfile) as fh:
        current_char = None
        line_acc = []
        for rl in fh:
            line = rl.strip()
            if line.startswith('#'):
                continue
            if line.endswith(':') and (line.startswith('0x') or line.startswith('u+')):
                if current_char is not None:
                    font[current_char] = line_acc
                    line_acc = []
                current_char = chr(int(line[2:-1], 16))
            elif ('.' in line or '@' in line) and not ':' in line:
                line_acc.append(line.replace('@', '1'))
        if current_char is not None:
            font[current_char] = line_acc
    return font

def parse_draw_font(fontfile):
    font = {}
    with open(fontfile) as fh:
        current_char = None
        line_acc = []
        for rl in fh:
            line = rl.strip()
            if len(line) > 2 and line[2] == ':':
                if current_char is not None:
                    font[current_char] = line_acc
                    line_acc = []
                current_char = chr(int(line[0:2], 16))
                if len(line) > 3:
                    line_acc.append(line[3:].strip().replace('#', '1').replace('-', '.'))
            elif '-' in line or '#' in line:
                line_acc.append(line.replace('#', '1').replace('-', '.'))
        if current_char is not None:
            font[current_char] = line_acc
    return font

def parse_font(fontfile):
    if fontfile.endswith('.yaff'):
        return parse_yaff_font(fontfile)
    if fontfile.endswith('.draw'):
        return parse_draw_font(fontfile)
    raise TypeError('Unknown font type.')

def find_and_load_font(font):
    try_font = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', f'{font}.yaff')
    if os.path.exists(try_font):
        font = try_font
    elif not os.path.exists(font):
        raise FileNotFoundError('Could not find font file.')
    return parse_font(font)

def pad_character_to_height(char_data, min_height, min_length=0):
    height = len(char_data)
    filler_line = '.' * min_length
    if height < min_height:
        diff = min_height - height
        for _ in range(diff // 2 + diff % 2):
            char_data.insert(0, filler_line)
        for _ in range(diff // 2):
            char_data.append(filler_line)
    return char_data

def pad_row_to_width(row_data, min_width, align=Align.CENTER):
    width = len(row_data)
    remaining = min_width - width
    if remaining > 0:
        if align == Align.LEFT:
            return row_data + ('.' * remaining)
        if align == Align.CENTER:
            return ('.' * (remaining // 2)) + row_data + ('.' * (remaining // 2 + remaining % 2))
        if align == Align.RIGHT:
            return ('.' * remaining) + row_data
    return row_data

def find_char_in_font(char, font_data):
    try:
        return font_data[char]
    except KeyError:
        if '\ufffd' in font_data:
            return font_data['\ufffd']
        elif '\x00' in font_data:
            return font_data['\x00']
        else:
            return font_data[' ']

def create_font_characters(text, font_data, min_height=12):
    font_characters = []
    for char in text:
        char_data = find_char_in_font(char, font_data)
        height = len(char_data)
        width = len(char_data[0])
        if height < min_height:
            pad_character_to_height(char_data, min_height)
            height = min_height
        if width < height:
            width = height
        font_characters.append(FontCharacterData(width, height, char, gen_bitmap(*char_data, min_len=width)))
    return font_characters

def reflow_text(text, font_data, width=48):
    lines = text.replace('\r', '').split('\n')
    wrapped_lines = []
    for line in lines:
        current_line = ''
        remaining_width = width
        for i, orig_word in enumerate(line.split(' ')):
            if i != 0:
                word = ' ' + orig_word
            else:
                word = orig_word

            text_width = sum(len(find_char_in_font(char, font_data)[0]) for char in word)
            if remaining_width - text_width >= 0:
                remaining_width -= text_width
                current_line += word
            elif text_width > width:
                for char in word:
                    char_width = len(find_char_in_font(char, font_data)[0])
                    if remaining_width - char_width >= 0:
                        remaining_width -= char_width
                        current_line += char
                    else:
                        wrapped_lines.append(current_line)
                        remaining_width = width - char_width
                        current_line = char
            else:
                wrapped_lines.append(current_line)
                text_width = sum(len(find_char_in_font(char, font_data)[0]) for char in orig_word)
                remaining_width = width - text_width
                current_line = orig_word
        wrapped_lines.append(current_line)
    return wrapped_lines

def lines_to_frames(lines, font_data, align=Align.CENTER, width=48, lines_per_frame=2, line_height=6):
    raster_lines = []
    for line in lines:
        raster_line = ['' for _ in range(line_height)]
        for char in line:
            char_data = find_char_in_font(char, font_data)
            height = len(char_data)
            if height > line_height:
                raise ValueError('Character height exceeds line height.')
            if height < line_height:
                pad_character_to_height(char_data, line_height, len(char_data[0]))
            for i, char_line in enumerate(char_data):
                raster_line[i] += char_line
        while len(raster_line[0]) > width:
            overflow_line = []
            for i in range(len(raster_line)):
                overflow_line.append(raster_line[i][:width])
                raster_line[i] = raster_line[i][width:]
            raster_lines.append(overflow_line)
        if len(raster_line[0]) < width:
            for i in range(len(raster_line)):
                raster_line[i] = pad_row_to_width(raster_line[i], width, align)
        raster_lines.append(raster_line)
    raster_frames = []
    current_frame = []
    current_frame_line_length = 0
    for raster_line in raster_lines:
        if current_frame_line_length < lines_per_frame:
            current_frame.extend(raster_line)
            current_frame_line_length += 1
        else:
            raster_frames.append(current_frame)
            current_frame = raster_line
            current_frame_line_length = 1
    if len(current_frame) > 0:
        if current_frame_line_length < lines_per_frame:
            for _ in range(lines_per_frame - current_frame_line_length):
                current_frame.extend(['.' * width for _ in range(line_height)])
        raster_frames.append(current_frame)

    return raster_frames

class LedConnection:
    def __init__(self, address):
        self.connection = GATTRequester(address)
        self._ensure_connection()
        self.connection.write_by_handle(0x0f, b'\x00\x00\x00\x01') # request notifications
        self.connection.on_notification = lambda handle, data: self._on_notification(handle, data)
        self.cmd_handle, self.data_handle = _discover_handles(self.connection)
        
        self.current_wait_event = Event()
        self.last_data = None
        self.data_serial_no = 0
        self.command_serial_no = 0

    def _on_notification(self, handle, data):
        if handle == self.cmd_handle:
            self.last_data = data
            self.current_wait_event.set()
    
    def _next_data_serial_no(self):
        self.data_serial_no = (self.data_serial_no + 1) & 0xffffffff
        return self.data_serial_no

    def _next_command_serial_no(self):
        self.command_serial_no = (self.command_serial_no + 1) & 0xffff
        return self.command_serial_no

    def _ensure_connection(self):
        if not self.connection.is_connected():
            try:
                self.connection.connect()
            except:
                # will sometimes throw if already trying to connect
                pass
            for _ in range(50):
                if self.connection.is_connected():
                    break
                time.sleep(0.1)
            else:
                raise TimeoutError("Timeout exceeded waiting for bluetooth connection.")

    def send_command(self, command):
        """
        Send a control command to the device.
        Used for basic commands and data sending flow control.
        """
        self._ensure_connection()
        self.current_wait_event.clear()
        self.connection.write_cmd(self.cmd_handle, command.serialize())
    
    def wait_for_response(self, timeout=0.2):
        """
        Wait for and return a response, usually from a command sent via send_command.
        """
        if not self.current_wait_event.wait(timeout):
            raise TimeoutError("Timeout exceeded waiting for GATT response.")
        return getCommandResponse(self.last_data)

    def _send_data_internal(self, data_command, timeout=0.2):
        """
        Send a data command to the device.
        Currently only SendDataCommand is used, which accepts raw serialized data.
        """
        self._ensure_connection()
        data_command.serial_no = self._next_data_serial_no()
        serial_no = self._next_command_serial_no()

        payload = data_command.serialize()
        self.send_command(SendingDataStartCommand(serial_no, data_command.command_type, len(payload)))
        response = self.wait_for_response(timeout)
        assert type(response) == SendingDataResponse
        assert response.serial_no == serial_no
        assert response.command_type == data_command.command_type
        assert response.error_code == 0

        seek = 0
        sent_payloads = 0
        send_size = 20
        send_count = 6

        while seek < len(payload):
            self.current_wait_event.clear()
            self.connection.write_cmd(self.data_handle, payload[seek:seek+send_size])
            sent_payloads += 1
            seek += send_size

            if sent_payloads >= send_count:
                sent_payloads = 0
                response = self.wait_for_response(timeout)
                assert type(response) == ContinueSendingResponse
                assert response.serial_no == serial_no
                assert response.command_type == data_command.command_type
                seek = response.continue_from
        
        self.send_command(SendingDataFinishCommand(serial_no, data_command.command_type, len(payload)))
        self.wait_for_response(timeout)

    def send_data(self, data_command, timeout=0.2, attempts=5):
        for i in range(attempts + 1):
            try:
                self._send_data_internal(data_command, timeout)
                return
            except TimeoutError:
                if i == attempts:
                    raise
                self.connection.disconnect()

    def set_brightness(self, brightness):
        """
        Sets the display brightness. 0 is lowest and 100 is highest.
        """
        self.send_data(SendDataCommand(BrightnessData(brightness).serialize()))

    def set_screen_mode(self, mode: ScreenMode):
        """
        This allows flipping and mirroring the display. See ScreenMode Enum.
        """
        self.send_data(SendDataCommand(ScreenModeData(mode.value).serialize()))

    def set_text_by_chars(self, text, effect=Effect.SCROLL_LEFT, font="6x12", speed=0, min_height=12, char_limit=72):
        """
        Sends text as characters. The device decides how to display them.
        This tends to be slower and more limited than set_text which sends the text as an animation.
        """
        if len(text) > char_limit:
            raise ValueError("The text exceeds the device character limit.")

        font_data = find_and_load_font(font)
        font_characters = create_font_characters(text, font_data, min_height)
        font_character_data = SendDataCommand(FontData(font_characters).serialize())
        text_data = SendDataCommand(TextData(text, speed, effect).serialize())
        self.send_data(font_character_data)
        self.send_data(text_data)

    def set_text_lines(self, text, align=Align.CENTER, font="4x6", frame_duration=2, width=48,
            lines_per_frame=2, line_height=6, effect=Effect.NONE, speed=20, reflow=True,
            frame_limit=20):
        """
        Sends multi-line text as an animation. Can pack two lines of text onto the display.
        """
        font_data = find_and_load_font(font)

        if reflow:
            lines = reflow_text(text, font_data, width)
        else:
            lines = text.replace('\r', '').split('\n')

        frames = lines_to_frames(lines, font_data, align, width, lines_per_frame, line_height)
        if len(frames) > frame_limit:
            raise ValueError("The animation exceeds the device frame limit.")

        height = lines_per_frame * line_height
        frame_data = SendDataCommand(
            AnimationData(
                [FrameData(width, height, gen_bitmap(*frame)) for frame in frames],
                int(frame_duration * 1000),
                speed,
                effect
            ).serialize()
        )

        self.send_data(frame_data)

    def set_text(self, text, effect=Effect.SCROLL_LEFT, font="6x12", speed=0, min_height=12):
        """
        Sends single-line scrolling text as an animation.
        """
        self.set_text_lines(
            text,
            Align.LEFT,
            font,
            lines_per_frame=1,
            line_height=min_height,
            effect=effect,
            speed=speed,
            reflow=False
        )

    def clear(self, width=48, height=12):
        """
        Clears the display by sending an empty frame.
        """
        frame_data = SendDataCommand(
            AnimationData(
                [FrameData(width, height, b'\x00' * int(width * height / 8))],
                0,
                0,
                Effect.NONE
            ).serialize()
        )

        self.send_data(frame_data)

    def disconnect(self):
        self.connection.disconnect()
