class Logger:
    _logging = False

    @classmethod
    def on(cls):
        Logger._logging = True

    @classmethod
    def off(cls):
        Logger._logging = False

    @classmethod
    def log(cls, fn):
        Logger.on()
        return fn

    @classmethod
    def _handle_last(cls, fn):
        Logger.off()

    @classmethod
    def info(cls, msg: str):
        print(f"[Info] {msg}")

    @classmethod
    def debug(cls, msg: str):
        if Logger._logging:
            print(f"[Debug] {msg}")

    @classmethod
    def warn(cls, msg: str):
        print(f"[Warn] {msg}")
