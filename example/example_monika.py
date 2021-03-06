from spotled import SendDataCommand, AnimationData, FrameData, gen_bitmap, LedConnection, Effect

default_monika = FrameData(48, 12, gen_bitmap(
    '11111..............1.....1......................'
    '..1...........1....11...11.............1........'
    '..1..........111...11...11...........1.1........'
    '..1.1..1..11..1....1.1.1.1..11...11....1..1..11.'
    '..1.1..1.1..1.1....1.1.1.1.1..1.1..1...1..1.1..1'
    '..1.1..1.1....1....1.1.1.1.1..1.1..1.1.1.1.....1'
    '..1.1..1..11..1....1..1..1.1..1.1..1.1.11....111'
    '..1.1..1....1.1....1..1..1.1..1.1..1.1.1.1..1..1'
    '..1.1..1.1..1.1....1..1..1.1..1.1..1.1.1..1.1..1'
    '.11..11...11...1...1.....1..11..1..1.1.1..1..111'
    '................................................'
    '................................................'
))

corrupt_monika_1 = FrameData(48, 12, gen_bitmap(
    '11111...........1..1..1..1...................111'
    '..1........1..1.11.1111.11..........1..1.......1'
    '..1..........111...11...11.............1........'
    '..1.1..1..11..1....1.1.1.1..1....11....1..1..11.'
    '.1111.1111.1111...1111111111.1111.11..11.1111.11'
    '.1111.1111...11...1111111111.1111..1111111.11111'
    '..1.1..1..11..1....1..1..1.1..1.1..1.1.11...1..1'
    '..1.1..1....1.1....1..1..1.1..1.1..1.1.1.1..1..1'
    '1.1.1..1.1..1.1....1..1..1.1..1.1..1.1.1..1.1.11'
    '.11..11...11...1...1.....1..11..1..1.1.1..1..1.1'
    '................................................'
    '................................................'
))

corrupt_monika_2 = FrameData(48, 12, gen_bitmap(
    '11111.............11....11.....................1'
    '.11..........11...111..111............11........'
    '.11.........1111..111..111..........1111........'
    '.1111.11.111.11...11111111.111..111...11.11.111.'
    '.1111.1111.1111...1111111111.1111.11..11.1111.11'
    '.1111.1111...11...1111111111.1111.11111111.11111'
    '.1111.11.111.11...11.11.1111.1111.1111111..11.11'
    '.1111.11...1111...11.11.1111.1111.11111111.11.11'
    '11111.1111.1111...11.11.1111.1111.111111.1111111'
    '111.111..111..11..11....11.111.11.111111.11.1111'
    '................................................'
    '................................................'
))

corrupt_monika_3 = FrameData(48, 12, gen_bitmap(
    '111111.............11....11.....................'
    '..11..........11...111..111............11.......'
    '..11.........1111..111..111..........1111.......'
    '..1111.11.111.11...11111111.111..111...11.11.111'
    '11.1111.1111.1.11.1.1.1.1.1111.111..1..111.111.1'
    '1.1111.1111...11...1111111111.1111.11111111.1111'
    '1.11.1.11.111111.1..1.11.11.1.11.1.11.1.1111.1.1'
    '1.1111.11...1111...11.11.1111.1111.11111111.11.1'
    '111111.1111.1111...11.11.1111.1111.111111.111111'
    '1111.111..111..11..11....11.111.11.111111.11.111'
    '................................................'
    '................................................'
))

corrupt_monika_4 = FrameData(48, 12, gen_bitmap(
    '11111111....1...1.111111.1......111.1111......1.'
    '1.111111......1.1.11111111......111.1111......1.'
    '1.111111.....1111.11111111......1.1.1111......1.'
    '1.1111111.111.111.111111111.111.111111111.11.111'
    '1.111111111.11111.11111111111.11111111111.111111'
    '1.111111111...111.11111111111.1111111111111.1111'
    '1.111111..11..1.1.111111.1.1..1.111111111...1..1'
    '1.111111....1.1.1.111111.1.1..1.1.111111.1..1..1'
    '1.111111.1..1.1.1.111111.1.1..1.11111111..1.1.11'
    '111111111111.1.111111111.111111.111111111.11.1.1'
    '1.111111......1.1.111111........1.1.1111......1.'
    '1.111111......1.11111111........1.1.1111......1.'
))

corrupt_monika_5 = FrameData(48, 12, gen_bitmap(
    '11111..............1.....1......................'
    '..1...........1....11...11.............1........'
    '..1..........111...11...11...........1.1........'
    '..1.1..1..11..1....1.1.1.1..11...11....1..1..11.'
    '..1.1..1.1..1.1....1.1.1.1.1..1.1..1...1..1.1..1'
    '..1.1..1.1....1....1.1.1.1.1..1.1..1.1.1.1..1111'
    '..1.1..1..11..1....1..1..1.1..1.1..1.1.11...1..1'
    '..1.1..1....1.1....1..1..1.1..1.1..1.1.1.1..1..1'
    '111.1.11.1.11.1.1..1.11.11.1.11.1.11.1.1.11.1.11'
    '111.111..111..11..11....11.111.11.111111.11.1111'
    '................................................'
    '................................................'
))

monika_command = SendDataCommand(
    AnimationData(
        [
            default_monika,
            default_monika,
            default_monika,
            corrupt_monika_1,
            default_monika,
            default_monika,
            corrupt_monika_2,
            default_monika,
            default_monika,
            default_monika,
            corrupt_monika_3,
            default_monika,
            default_monika,
            corrupt_monika_4,
            default_monika,
            default_monika,
            default_monika,
            corrupt_monika_5
        ], 130, 9, Effect.NONE
    ).serialize()
)

if __name__ == '__main__':
    import sys
    sender = LedConnection(sys.argv[1])
    sender.send_data(monika_command)
