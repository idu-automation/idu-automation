import locaters
from health_check import HealthCheck
from login import Login
from utils import Utils
from maintenance_functionalities import Maintenance
from wireless import Wireless

from logger import setup_logger
logger = setup_logger( __name__ )

class FunctionalSanity:
    def __init__(self,driver):
        self.driver = driver
        self.utils=Utils(driver)
        self.health=HealthCheck(driver)
        self.maintenance = Maintenance(driver)
        self.login=Login(driver)

    def functional_sanity_06(self):
        logger.debug( "======================================================================================" )
        logger.debug( 'Validating MAC Address after Reboot and Reset' )
        try:
            if self.health.health_check_webgui() == False:
                logger.error( 'Device health check failed. Exiting the test.' )
                return False

            #Getting wan mac address before reboot and reset
            self.utils.search_WebGUI("WAN Information")
            wan_mac_address = self.utils.find_element( *locaters.WanInfo_MacAddress ).text
            logger.debug( f'WAN MAC Address before Reboot: {wan_mac_address}' )

            # Rebooting Device
            self.maintenance.reboot()
            self.login.WebGUI_login()

            #Getting wan mac address after reboot
            self.utils.search_WebGUI( "WAN Information" )
            wan_mac_address_after_reboot = self.utils.find_element( *locaters.WanInfo_MacAddress ).text
            logger.debug( f'WAN MAC Address after Reboot: {wan_mac_address_after_reboot}' )

            success = 0
            if wan_mac_address == wan_mac_address_after_reboot:
                success += 1
                logger.info( 'WAN MAC Address is same after Reboot ' )
            else:
                logger.error( 'WAN MAC Address has changed after Reboot' )
                self.utils.get_DBGLogs()

            # Reseting Device
            self.maintenance.reset()
            self.login.WebGUI_login()

            # Getting wan mac address after reset
            self.utils.search_WebGUI( "WAN Information")
            wan_mac_address_after_reset = self.utils.find_element( *locaters.WanInfo_MacAddress  ).text
            logger.debug( f'WAN MAC Address after Reset: {wan_mac_address_after_reset}' )

            if wan_mac_address == wan_mac_address_after_reset:
                success += 1
                logger.info( 'WAN MAC Address is same after Factory Reset' )
            else:
                logger.error( 'WAN MAC Address has changed after Factory Reset' )
                self.utils.get_DBGLogs()


            if success == 2:
                logger.info( 'MAC Address is same after Reboot and Reset' )
                return True
            else:
                logger.error( 'MAC Address has changed after Reboot or Reset' )
                return False

        except Exception as e:
            logger.error( "Error occurred while executing functional_sanity_06: %s" , str( e ) )
            self.utils.get_DBGLogs()
            return False


        self.wireless = Wireless(driver)

    #Multiple Reset
    def functional_sanity_58(self):
        logger.debug("======================================================================================")
        logger.info("Validating multiple factory reset")
        try:
            if self.health.health_check_webgui() == False:
                logger.error('Device health check failed. Exiting the test.')
                return False
            n = 5
            for i in range(n):
                logger.debug( f"-------------{i + 1}th Factory Reset---------------------" )
                self.maintenance.reset()

                if self.health.health_check_webgui() == False:
                    logger.error('Device health check failed. Exiting the test.')
                    logger.error(f"Error occurred after {i + 1}th factory reset iteration")
                    self.utils.get_DBGLogs()
                    return False

            logger.info(f"Successfully factory reset from Web GUI - {n} Iterations")
            return True
        except Exception as E:
            logger.error(f"Error occurred during functional_sanity_58: {str(E)}")
            self.utils.get_DBGLogs()
            return False

    #Multiple Reboot
    def functional_sanity_01(self):
        logger.debug("======================================================================================")
        logger.info("Validating multiple reboot")
        n = 2
        try:
            if self.health.health_check_webgui() == False:
                logger.error('Device health check failed. Exiting the test.')
                return False

            self.wireless.set_ssid_password_from_gui()

            for i in range(n):
                logger.debug( f"-------------{i + 1}th Reboot---------------------" )
                self.maintenance.reboot()

                if self.health.health_check_webgui() == False:
                    logger.error('Device health check failed. Exiting the test.')
                    logger.error(f"Error occurred after {i + 1}th reboot iteration")
                    self.utils.get_DBGLogs()
                    return False
                ssid_from_gui = self.wireless.get_ssid_from_gui()
                if ssid_from_gui == input.test_ssid:
                    logger.info(f'SSID post reboot is the same: {ssid_from_gui}')
                else:
                    logger.error(f'SSID post reboot is not the same. '
                                 f'Expected:{input.test_ssid}, Actual:{ssid_from_gui}')
                    return False

            logger.info(f"Successfully reboot from WebGUI - {n} Iterations")
            return True
        except Exception as E:
            logger.error(f"Error occurred during functional_sanity_01: {str(E)}")
            self.utils.get_DBGLogs()
            return False
