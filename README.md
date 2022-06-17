# SPOTLED Python Library

This allows you to control bluetooth led name badges which use the SPOTLED app. You can buy them here:

 - https://smile.amazon.com/gp/product/B07YD4DM1Y/
 - https://a.aliexpress.com/_mt5JedG

## Disclaimer

Notice! This library is not affilated with the creator of this product.

If you brick your device (albeit unlikely) with this library, DO NOT BLAME ME!

## Installation

You need [python3-gattlib](https://pypi.org/project/gattlib/), which is installable on debian with:

```bash
sudo apt install python3-gattlib
```

Then install the package with:

```bash
sudo pip3 install spotled
```

## Example usage

```python
import spotled
sender = spotled.LedConnection('mac address of your device')

sender.set_screen_mode(spotled.ScreenMode.NORMAL) # change screen orientation
sender.set_brightness(100) # brightness seems to be 0-100

# send text using the default 6x12 font
sender.set_text('Hello world!')

# send text which does not move
sender.set_text(' Static', effect=spotled.Effect.NONE)

# send smaller text (you can use any 12x12 or smaller yaff or draw font)
sender.set_text('Static Text!', effect=spotled.Effect.NONE, font="4x6")

# send multiple pages of 2-line text
# you can adjust time per frame with the frame_duration param
sender.set_text_lines("You can show several pages of text!\nNewlines\nare allowed.")

# send multiple pages of scrolling 2-line text
# you can adjust animation speed with the speed param
sender.set_text_lines("A long time ago in a galaxy far, far away....", effect=spotled.Effect.SCROLL_UP)

# send number bars (used for music visualization)
sender.send_data(spotled.SendDataCommand(spotled.NumberBarData([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 11, 10, 9]).serialize()))

# send a static image (using the animation feature)
sender.send_data(
    spotled.SendDataCommand(
        spotled.AnimationData([
            spotled.FrameData(48, 12, spotled.gen_bitmap(
                '111111111111111111111111111111111111111111111111'
                '1..............................................1'
                '1..............................................1'
                '1..............................................1'
                '1..............................................1'
                '1..............................................1'
                '1..............................................1'
                '1..............................................1'
                '1..............................................1'
                '1..............................................1'
                '1..............................................1'
                '111111111111111111111111111111111111111111111111'
            ))
        ], 0, 0, spotled.Effect.NONE).serialize()
    )
)
```

See the `example_monika.py` file for an example animation and `example_pepsi.py` for an example
scrolling bitmap text display. You can replay existing payloads from Wireshark as well fairly
easily by using the `SendDataCommand` and chopping off the header (first 15 bytes).

Fonts from this software are from https://www.cl.cam.ac.uk/~mgk25/ucs-fonts.html and are public domain.

You can get more fonts here: https://github.com/robhagemans/hoard-of-bitfonts
