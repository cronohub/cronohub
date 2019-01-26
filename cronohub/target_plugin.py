from abc import ABCMeta, abstractmethod


class CronohubTargetPlugin(metaclass=ABCMeta):
    """
    This is the basic definition of a CronoHub plugin.
    """
    @abstractmethod
    def validate(self):
        ...

    @abstractmethod
    def help(self):
        ...

    @abstractmethod
    def archive(self, files):
        ...
