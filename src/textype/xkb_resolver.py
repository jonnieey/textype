# xkb_resolver.py
import xkbcommon.xkb as xkb


class XKBResolver:
    def __init__(self):
        self.ctx = xkb.Context()
        self.keymap = self.ctx.keymap_new_from_names()
        self.state = self.keymap.state_new()

    def update_modifiers(self, shift=False, altgr=False):
        mods = 0

        def mod(name):
            return self.keymap.mod_get_index(name)

        if shift:
            mods |= 1 << mod("Shift")
        if altgr:
            mods |= 1 << mod("ISO_Level3_Shift")

        self.state.update_mask(mods, 0, 0, 0, 0, 0)

    def resolve(self, evdev_code: int) -> str | None:
        xkb_code = evdev_code + 8  # IMPORTANT
        sym = self.state.key_get_one_sym(xkb_code)
        if sym == xkb.lib.XKB_KEY_NoSymbol:
            return None
        return xkb.keysym_to_string(sym)
