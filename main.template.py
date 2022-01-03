from GreenPonik_BLE.gattserver import BleApplication, JsonAdvertisement, JsonService
import os

if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

app = BleApplication()

app.add_service(JsonService(0))
app.register()

adv = JsonAdvertisement(0)
adv.register()

try:
    app.run()
except KeyboardInterrupt:
    app.quit()
