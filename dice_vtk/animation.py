from dice_tools import wizard, process_messages


class VtkSceneAnimation:
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__playing = False
        self.__frame = 0
        self.__times = []
        self.__loop = False
        
    def update(self, time):
        pass

    @property
    def playing(self):
        return self.__playing

    @property
    def frame(self):
        return self.__frame

    @property
    def frames_count(self):
        return len(self.__times)

    @property
    def times(self):
        return self.__times

    @times.setter
    def times(self, times):
        if self.__times != times:
            self.__times = times
            wizard.w_animation_times_changed(self)

    @property
    def loop(self):
        return self.__loop

    @loop.setter
    def loop(self, loop):
        if self.__loop != loop:
            self.__loop = loop
            wizard.w_animation_loop_changed(self)

    def set_time(self, time):
        try:
            frame = self.__times.index(time)
        except ValueError:
            return False
        self.update(time)
        self.__frame = frame
        wizard.w_animation_frame_changed(self, frame)
        return True

    def set_frame(self, frame):
        try:
            time = self.__times[frame]
        except IndexError:
            return False
        self.update(time)
        if frame < 0:
            frame = len(self.__times) + frame
        self.__frame = frame
        wizard.w_animation_frame_changed(self, frame)
        return True

    def play(self):
        if not self.__playing:
            self.__playing = True
            wizard.w_animation_playing_changed(self, True)
            while self.__playing:
                if (not self.set_frame(self.__frame+1) and
                    (not self.__loop or not self.set_frame(0))):
                        self.__playing = False
                        wizard.w_animation_playing_changed(self, False)
                else:
                    process_messages()

    def stop(self):
        self.__playing = False