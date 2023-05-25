from abc import ABC, abstractmethod

class VPN(ABC):
    def __init__(self, config_file: str):
        """
        Initialize the VPN instance with a configuration file.
        """
        self.config_file = config_file

    @abstractmethod
    def setup(self):
        """
        Setup the VPN connection.
        """
        pass
    
    @abstractmethod
    def get_interface(self):
        """
        Get the interface name used by the VPN connection.
        """
        pass

    @abstractmethod
    def get_ip(self):
        """
        Get the IP address assigned by the VPN connection.
        """
        pass
    
    @abstractmethod
    def get_info(self):
        """
        Get the information about the VPN connection.
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Disconnect the VPN connection.
        """
        pass

    @abstractmethod
    def reconnect(self):
        """
        Reconnect the VPN connection.
        """
        pass
