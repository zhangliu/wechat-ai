from zlExt.utils.logger import log

def exit_callback(self):
    log('[zlExt] Logout! will try login...')
    self.startup()