# SPOTLED Python Library

This allows you to control bluetooth led name badges which use the SPOTLED app. You can buy them here:

 - https://smile.amazon.com/gp/product/B07YD4DM1Y/
 - https://a.aliexpress.com/_mt5JedG

## Disclaimer

Notice! This library is not affilated with the creator of this product.

If you brick your device (albeit unlikely) with this library, DO NOT BLAME ME!

## Example usage

```python
import spotled
sender = spotled.LedConnection('mac address of your device')

sender.set_screen_mode(spotled.ScreenMode.NORMAL) # change screen orientation
sender.set_brightness(100) # brightness seems to be 0-100

sender.send_data(spotled.SendDataCommand(SomeData().serialize()))
```

See the `example_monika.py` file for an example animation and `example_pepsi.py` for an example
scrolling bitmap text display. You can replay existing payloads from Wireshark as well fairly
easily by using the `SendDataCommand` and chopping off the header (first 15 bytes).
