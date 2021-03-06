from spotled import FontCharacterData, SendDataCommand, FontData, TextData, gen_bitmap, LedConnection, Effect

pepsi_font_command = SendDataCommand(
    FontData([
        FontCharacterData(12, 12, 'D', gen_bitmap(
            '.....',
            '.....',
            '1111.',
            '.1..1',
            '.1..1',
            '.1..1',
            '.1..1',
            '.1..1',
            '.1..1',
            '1111.',
            '.....',
            '.....',
            min_len=16
        )),
        FontCharacterData(12, 12, 'r', gen_bitmap(
            '.....',
            '.....',
            '.....',
            '.....',
            '.....',
            '11.11',
            '.11..',
            '.1...',
            '.1...',
            '111..',
            '.....',
            '.....',
            min_len=16
        )),
        FontCharacterData(12, 12, 'i', gen_bitmap(
            '....',
            '..1.',
            '..1.',
            '....',
            '....',
            '.11.',
            '..1.',
            '..1.',
            '..1.',
            '.111',
            '....',
            '....',
            min_len=16
        )),
        FontCharacterData(12, 12, 'n', gen_bitmap(
            '......',
            '......',
            '......',
            '......',
            '......',
            '1111..',
            '.1..1.',
            '.1..1.',
            '.1..1.',
            '111.11',
            '......',
            '......',
            min_len=16
        )),
        FontCharacterData(12, 12, 'k', gen_bitmap(
            '.....',
            '11...',
            '.1...',
            '.1...',
            '.1...',
            '.1.11',
            '.1.1.',
            '.11..',
            '.1.1.',
            '11..1',
            '.....',
            '.....',
            min_len=16
        )),
        FontCharacterData(12, 12, ' ', b'\x00' * 24),
        FontCharacterData(12, 12, 'P', gen_bitmap(
            '.....',
            '.....',
            '1111.',
            '.1..1',
            '.1..1',
            '.111.',
            '.1...',
            '.1...',
            '.1...',
            '111..',
            '.....',
            '.....',
            min_len=16
        )),
        FontCharacterData(12, 12, 'e', gen_bitmap(
            '.....',
            '.....',
            '.....',
            '.....',
            '.....',
            '..11.',
            '.1..1',
            '.1111',
            '.1...',
            '..111',
            '.....',
            '.....',
            min_len=16
        )),
        FontCharacterData(12, 12, 'p', gen_bitmap(
            '.....',
            '.....',
            '.....',
            '.....',
            '.....',
            '1111.',
            '.1..1',
            '.1..1',
            '.1..1',
            '.111.',
            '.1...',
            '111..',
            min_len=16
        )),
        FontCharacterData(12, 12, 's', gen_bitmap(
            '.....',
            '.....',
            '.....',
            '.....',
            '.....',
            '.1111',
            '.1...',
            '..11.',
            '....1',
            '.1111',
            '.....',
            '.....',
            min_len=16
        )),
        FontCharacterData(12, 12, 'i', gen_bitmap(
            '....',
            '..1.',
            '..1.',
            '....',
            '....',
            '.11.',
            '..1.',
            '..1.',
            '..1.',
            '.111',
            '....',
            '....',
            min_len=16
        )),
        FontCharacterData(12, 12, ' ', b'\x00' * 24)
    ]).serialize()
)

pepsi_command = SendDataCommand(TextData('Drink Pepsi ', 0, Effect.SCROLL_LEFT).serialize())

if __name__ == '__main__':
    import sys
    sender = LedConnection(sys.argv[1])
    sender.send_data(pepsi_font_command)
    sender.send_data(pepsi_command)
