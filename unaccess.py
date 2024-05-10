import winreg
import os

def add_drivers_to_firewall(driver_names):
    try:
        # Define the path to the firewall rules in the registry
        firewall_reg_path = r"SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\StandardProfile\AuthorizedApplications\List"
        
        # Open the firewall registry key with write access
        firewall_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, firewall_reg_path, 0, winreg.KEY_ALL_ACCESS)

        for driver_name in driver_names:
            # Define the full path to the driver
            driver_path = f"{os.environ['SystemRoot']}\\System32\\drivers\\{driver_name}"
            driver_value_name = f"{driver_path}:*:Enabled:{driver_name}"

            try:
                # Try to retrieve the existing registry entry
                existing_value, _ = winreg.QueryValueEx(firewall_key, driver_value_name)
                print(f"{driver_name} already exists in the firewall list: {existing_value}")
            except FileNotFoundError:
                # If the entry does not exist, create it
                winreg.SetValueEx(firewall_key, driver_value_name, 0, winreg.REG_SZ, driver_path)
                print(f"Added {driver_name} to the firewall list at {driver_path}")

        # Close the firewall registry key
        winreg.CloseKey(firewall_key)
        print("Done! The specified drivers will no longer be flagged as incompatible in the firewall.")

    except Exception as e:
        print(f"Error: Unable to access or modify the firewall registry key: {str(e)}")

if __name__ == "__main__":
    driver_names = ["aow_drv_x64_ev.sys", "HoYoKProtect.sys", "UniFairy_x64.sys", "unirsdt.sys"]
    add_drivers_to_firewall(driver_names)
