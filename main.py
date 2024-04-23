from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.utils import platform
from components.functions import Database, ConnectionWebsite
from ntplib import NTPClient
from datetime import datetime, time
from kivy.clock import Clock

class Login(MDScreen):
    def __init__(self, user, pw, wb_instance, *args, **kwargs):
        super(Login, self).__init__(*args, **kwargs)
        self.wb_instance = wb_instance
        
        if user and pw:
            self.ids.email_text.text = user
            self.ids.password_text.text = pw
            self.ids.checkbox_user.active = True
            self.ids.checkbox_pw.active = True
        
        elif user:
            self.ids.email_text.text = user
            self.ids.checkbox_user.active = True
        
        elif pw:
            self.ids.password_text.text = pw
            self.ids.checkbox_pw.active = True

    def user(self):
        self.email = self.ids.email_text.text
        self.password = self.ids.password_text.text
        
        
        if self.email != "":
            if self.password != "":
                if self.ids.checkbox_user.active and self.ids.checkbox_pw.active:
                    Database().store_data(self.email, self.password)
                    
                elif self.ids.checkbox_user.active:
                    Database().store_user(self.email)
                    Database().delete_pw()
                    
                elif self.ids.checkbox_pw.active:
                    Database().store_pw(self.password)
                    Database().delete_user()
                    
                else:
                    Database().delete_data()
                
                self.login()
                    
            else:
                self.ids.password_text.hint_text_color_focus = "red"
                self.ids.password_text.hint_text_color_normal = "red"
                self.ids.password_text.hint_text = "Bitte Passwort eingeben"
                self.ids.password_text.text = ""

        else:

            self.ids.email_text.hint_text = "Gültige E-Mail Adresse eingeben!"
            self.ids.email_text.hint_text_color_focus = "red"
            self.ids.email_text.hint_text_color_normal = "red"
            self.ids.email_text.text = ""

    def login(self):
        login_status = self.wb_instance.login(self.email,self.password)
        
        if login_status:
            MDApp.get_running_app().select_screen()
            
                
        else:
            self.ids.email_text.hint_text = "Benutzername oder Passwort falsch"
            self.ids.email_text.hint_text_color_focus = "red"
            self.ids.email_text.hint_text_color_normal = "red"
            self.ids.email_text.text = ""
            self.ids.password_text.text = ""

class StartTime(MDScreen):
    def __init__(self, wb_instance, *args, **kwargs):
        super(StartTime, self).__init__(*args, **kwargs)
        self.wb_instance = wb_instance
    
    def build(self, data):
        self.ids.name.text = data["name"]

    def start(self):
        
        if self.ids.home_check.active:
            location = {"homeo": "1"}
        
        else:
            location = {"homeo": "2"}
        
        self.wb_instance.start(location)
        MDApp.get_running_app().select_screen()

class Time(MDScreen):
    def __init__(self, wb_instance, *args, **kwargs):
        super(Time, self).__init__(*args, **kwargs)
        self.wb_instance = wb_instance

    def build(self, data):
        self.ids.name.text = data["name"]
        self.ids.start_time.text = data["start_time"]
        self.show_dialog()

    def stop_time(self):
        self.app = MDApp.get_running_app()
        current_time = self.app.get_time()
        time_now = datetime.fromtimestamp(current_time).time()
        target_time = time(16,30,2)
        time_difference = datetime.combine(datetime.min, time_now) - datetime.combine(datetime.min, target_time)
        self.difference_seconds = time_difference.total_seconds() * -1
        if self.ids.target_time_check.active:
            self.ids.btn_end.text = "Autom. auloggen abbrechen!"
            self.ids.btn_end.on_press = lambda x = None: self.def_dialog("abort_auto")
            self.clock_stop = Clock.schedule_once(self.wb_instance.end, self.difference_seconds)
            self.clock_screen = Clock.schedule_once(self.app.select_screen, self.difference_seconds + 1)
            
        elif self.difference_seconds > 0:
            self.def_dialog("abort")
            
        else:
            self.wb_instance.end()
            self.app.select_screen()
    
    def def_dialog(self,def_dialog):
        
        if def_dialog == "abort_auto":
            self.dialog.title = "Automatisches ausloggen abbrechen?"
            self.dialog.text = ""
            self.dialog.buttons[1].text = "OK"
            self.dialog.buttons[1].on_release = self.abort_clock
        
        else:
            self.dialog.title = "Du willst schon gehen?"
            self.dialog.text = "\nDu wirst vor 16:30 ausgeloggt!"
            self.dialog.buttons[1].text = "Log mich aus"
            self.dialog.buttons[1].on_release = self.function_dialog
        
        self.dialog.open()

    def show_dialog(self):
        
        self.dialog = MDDialog(
            title = "",
            text = "",
            

            buttons=[
                MDFlatButton(
                    text = "Abbrechen",
                    theme_text_color = "Custom",
                    text_color = self.theme_cls.primary_color,
                    on_release = self.close_dialog
                ),
                MDFlatButton(
                    text = "self.btn_text",
                    theme_text_color = "Custom",
                    text_color = self.theme_cls.primary_color,
                    
                ),
            ],
        )
        
    
    def abort_clock(self, *args):
        self.clock_stop.cancel()
        self.clock_screen.cancel()
        self.ids.target_time_check.active = False
        self.ids.btn_end.text = "Ausloggen"
        self.ids.btn_end.on_press = lambda *args: None
        self.ids.btn_end.on_release = lambda *args: None
        self.ids.btn_end.on_release = self.stop_time
        self.close_dialog()
        
    def function_dialog(self, *args):
        self.wb_instance.end()
        self.app.select_screen()
        self.close_dialog()

    
    def close_dialog(self, *args):
        self.dialog.dismiss()

class EndTime(MDScreen):

    def build(self, data):
        self.ids.name.text = data["name"]
        self.ids.start_time.text = data["start_time"]
        self.ids.end_time.text = data["end_time"]

    def shutdown(self):  
        MDApp.get_running_app().stop()  

class OtherScreen(MDScreen):

    def build(self, data):
        self.ids.wb_message_text.text = data["message"] + "\nGuck nochmal auf der Webseite!\nHave Fun!"
        self.ids.name.text = data["name"]

class GFNLogin(MDApp):
    # Hier muss Sqllite abgefragt werden, ob gespeicherte Userdaten vorhanden sind, zudem findet hier der Abfrage eines NTP Server statt
    def __init__(self, **kwargs):
        super(GFNLogin, self).__init__(**kwargs)
        self.user_data = Database().get_data()
        self.wb_instance = ConnectionWebsite()

        
    def build(self):
        self.sm = MDScreenManager()
        self.sm.add_widget(Login(user = self.user_data[0], pw = self.user_data[1], wb_instance = self.wb_instance, name = "login"))
        self.sm.add_widget(StartTime(wb_instance = self.wb_instance, name = "start_time"))
        self.sm.add_widget(Time(wb_instance = self.wb_instance, name = "time"))
        self.sm.add_widget(EndTime(name = "end_time"))
        self.sm.add_widget(OtherScreen(name = "other_screen"))
        self.get_time()
        Clock.schedule_interval(self.update_label, 1)
        
        return self.sm

    def get_time(self):
        ntp = NTPClient()
        npt_time = ntp.request('pool.ntp.org', version=4)
        self.current_time = npt_time.tx_time
        return self.current_time
    
    def update_label(self,dt):
        self.current_time += dt
        time_now = datetime.fromtimestamp(self.current_time)
        formatted_time = time_now.strftime('%H:%M:%S')
        time_screen = self.sm.get_screen('time')
        time_start = self.sm.get_screen('start_time')
        time_end = self.sm.get_screen('end_time')
        time_other = self.sm.get_screen('other_screen')
        time_screen.ids.clock.text = formatted_time
        time_start.ids.clock.text = formatted_time
        time_end.ids.clock.text = formatted_time
        time_other.ids.clock.text = formatted_time
    
    def select_screen(self, *args):
        data = self.wb_instance.select_screen()
        screen_instance = self.sm.get_screen(data["screen"])
        screen_instance.build(data)
        self.sm.current = data["screen"]
    
    

if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.INTERNET,Permission.WRITE_EXTERNAL_STORAGE,Permission.READ_EXTERNAL_STORAGE])
    GFNLogin().run()

if platform == "win":
    GFNLogin().run()