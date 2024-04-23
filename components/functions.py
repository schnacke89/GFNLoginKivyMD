import os
import sqlite3
import requests
from bs4 import BeautifulSoup
from Crypto import Random
from Crypto.Cipher import AES
from base64 import b64encode, b64decode

class Database():
    def __init__(self):
        file_path = os.path.dirname(os.path.abspath(__file__))
        db_file = os.path.join(file_path, "user.db")
        self.conn_db = sqlite3.connect(db_file)
        self.db_cursor = self.conn_db.cursor()
        self.db_cursor.execute("CREATE TABLE IF NOT EXISTS user (id Integer Primary Key, email TEXT, pw TEXT)")
        self.db_cursor.execute("SELECT * FROM user")
        self.user = self.db_cursor.fetchall()

    def get_data(self):
        
        if len(self.user) == 0:
            self.db_cursor.execute("INSERT INTO user (email, pw) VALUES (NULL, NULL)")
            self.conn_db.commit()
            self.db_cursor.execute("SELECT * FROM user")
            self.user = self.db_cursor.fetchall()
            
            return self.user[0][1], self.user[0][2]
        
        else:
            
            if self.user[0][2]:
                pw = CryptData().decrypt_pw(self.user[0][2])
                
                return self.user[0][1], pw
            
            else:
                
                return self.user[0][1], self.user[0][2]
        
    def store_data(self, email, pw):
        pw = CryptData().encrypt_pw(pw)
        self.db_cursor.execute("UPDATE user SET email = ?, pw = ? WHERE id = 1", (email, pw))
        self.conn_db.commit()

    def store_user(self, email):
        self.db_cursor.execute("UPDATE user SET email = ? WHERE id = 1", (email,))
        self.conn_db.commit()

    def store_pw(self, pw):
        self.db_cursor.execute("UPDATE user SET pw = ? WHERE id = 1", (pw,))
        self.conn_db.commit()
    
    def delete_data(self):
        self.db_cursor.execute("UPDATE user SET email = NULL, pw = NULL WHERE id = 1")
        self.conn_db.commit()
    
    def delete_user(self):
        self.db_cursor.execute("UPDATE user SET email = NULL WHERE id = 1")
        self.conn_db.commit()

    def delete_pw(self):
        self.db_cursor.execute("UPDATE user SET pw = NULL WHERE id = 1")
        self.conn_db.commit()

class CryptData():

    def encrypt_pw(self, pw):
        pw_byte = pw.encode("utf-8")
        key = Random.get_random_bytes(32)
        nonce = Random.get_random_bytes(16)
        encryptor = AES.new(key, AES.MODE_SIV, nonce = nonce)
        pw_encrypted, tag = encryptor.encrypt_and_digest(pw_byte)
        decoded_data = [b64encode(x).decode("utf-8") for x in (pw_encrypted, key, nonce, tag)]
        storable_pw = ".".join(decoded_data)

        return storable_pw
    
    def decrypt_pw(self, stored_pw):
        stored_pw = stored_pw.split(".")
        encoded_data = [b64decode(x) for x in stored_pw]
        decryptor = AES.new(encoded_data[1], AES.MODE_SIV, nonce = encoded_data[2])
        pw_encoded = decryptor.decrypt_and_verify(encoded_data[0], encoded_data[3])
        pw = pw_encoded.decode("utf-8")
        
        return pw

class ConnectionWebsite():
    def __init__(self):
        self.url_login = 'https://lernplattform.gfn.de/login/index.php'
        self.url = 'https://lernplattform.gfn.de/' 
        self.header = {}
        self.session = requests.Session()

    def login(self, email, pw):
        request = self.session.get(self.url)
        token = BeautifulSoup(request.text, "html.parser")
        
        for card in token.select(".card-body"):
            self.header['logintoken'] = card.find('input',
                                            {'name':'logintoken'})['value']
        
        self.header["username"] = email
        self.header["password"] = pw
        response = self.session.post(self.url_login, self.header)
                
        if response.headers["Expires"]:
            
            return True
        
        else:
            
            return False
    
    def select_screen(self,*args):
        request = self.session.get(self.url)
        data_soup = BeautifulSoup(request.text, "html.parser")
        status = data_soup.find('input', 'btn-primary') #Attribut suche für Status1 = Zeiterfassung nicht gestartet
        status2 = data_soup.find('button', class_= 'btn-primary', string='Beenden') #Attribut suche für Status2 = Zeiterfassung gestartet
        status3 = data_soup.find(class_= 'alert')
        name = data_soup.find(id="actionmenuaction-1").text
        data = {"name": name}
       
        if status:
            data["screen"] = "start_time"
        
        elif status2:
            start_time = data_soup.select('p:-soup-contains("Startzeit")')[0].text.split(":", 1)[1].strip()
            data["start_time"] = start_time
            data["screen"] = "time"

           
            
        elif status3:
            data["screen"] = "other_screen"
            data["message"] = status3.text
        
        else:
            start_time = data_soup.select('p:-soup-contains("Startzeit")')[0].text.split(":", 1)[1].strip()
            end_time = data_soup.select('p:-soup-contains("Endzeit")')[0].text.split(":", 1)[1].strip()
            data["start_time"] = start_time
            data["end_time"] = end_time
            data["screen"] = "end_time"
            
        return data
    
    def start(self, location):
        start_url = self.url + "?=starten1"
        self.session.post(start_url, location)
    
    def end(self, *args):
        end_url = self.url + "?stoppen=1"
        self.session.get(end_url)
    
    
        