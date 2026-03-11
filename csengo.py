import time
import schedule
import vlc

from osztalyok import csengo_json

def schedule_actions():

  with open("csengo_config.json", "r") as file:
    tartalom = file.read()
    konfiguracio = csengo_json.CsengoKonfiguracio.model_validate_json(tartalom)

  for idopont in konfiguracio.idopontok:
    schedule.every().day.at(idopont.idopont).do(\
        job, \
        variable=idopont.zene if idopont.zene != None else konfiguracio.alapZene\
    )

  while True:
    schedule.run_pending()
    time.sleep(5)

def job(variable):
    print(f"Playing: {variable}")
    player = vlc.MediaPlayer(variable)
    player.play()
    time.sleep(10)
    player.stop()
    return

print("Scheduler is starting...")
schedule_actions()