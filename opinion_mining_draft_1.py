import json
import sys
import pandas
import numpy as np
import tweepy
import dataset
from stuf import stuf
import geopy
from twitter import *
from textblob import TextBlob
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QMessageBox

#format adapted from https://build-system.fman.io/pyqt5-tutorial

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.title = "App Main Screen"
        self.top = 100
        self.left = 100
        self.width = 624
        self.height = 415

        self.setWindowIcon(QtGui.QIcon("twitter.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)

        self.initUI()

    def initUI(self):
        self.label = QLabel(self)
        

        self.label.setPixmap(QPixmap('twitter.png'))
        self.label.setGeometry(0, 0, self.width, self.height)

        
        #self.show()

        self.b1 = QtWidgets.QPushButton('Start!', self)
        self.b1.move((self.top + self.height)/2, (self.left + self.width)/2)
        self.b1.setStyleSheet("background-color: white")
        self.b1.clicked.connect(self.search)

        # creating label 
        self.label1 = QLabel("Twitter Search Engine: Just enter a word or phrase you're curious about and see what people are feeling about it on Twitter!", self) 
  
        # setting geometry to the label 
        label1Width = 300
        label1Height = 80
        self.label1.setGeometry((self.width)/2 - (label1Width/2), (self.height)/4 - (label1Height/4), label1Width, label1Height) 
  
        # adding border to the label 
        self.label1.setStyleSheet("border : 2px solid black; background-color: white") 
  
        # making it multi line 
        self.label1.setWordWrap(True) 

        
    def search(self):
        self.searchWindow = SearchWindow()
        self.searchWindow.show()
        self.hide()

    def buttonPressed(self):
        self.label.setText("button is pressed!")
        self.update()

    def update(self):
        self.label.adjustSize()

        
class SearchWindow(QWidget):
    def __init__(self, parent = None):
        super(SearchWindow, self).__init__(parent)

        self.title = "Search Screen"
        self.top = 100
        self.left = 100
        self.width = 624
        self.height = 415

        self.setWindowIcon(QtGui.QIcon("twitter.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)

        self.initUI()

    def initUI(self):
        self.label = QLabel(self)

        self.label.setPixmap(QPixmap('twitter.png'))
        self.label.setGeometry(0, 0, self.width, self.height)


        self.layout = QtWidgets.QFormLayout()

       
        self.startButton = QtWidgets.QPushButton("search")

        self.startButton.clicked.connect(self.take_text_input)

        #INCLUDE HERE THE USER INPUT OF WHERE THEY ARE FROM
            #if they do not specify, then don't use the information


        self.lineEdit = QtWidgets.QLineEdit()
        self.layout.addRow(self.startButton,self.lineEdit)

        self.setLayout(self.layout)
      
    
    def showError(self):
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Critical)
        self.msg.setText("Error")
        self.msg.setInformativeText('More information')
        self.msg.setWindowTitle("Error")
        self.msg.exec_()


    def take_text_input(self):
        self.text, self.ok = QtWidgets.QInputDialog.getText(self, 'Twitter Search', 
            'How are people on Twitter feeling about...')
           
        #will make sure that self.text is initialized to some value (a.k.a. non-None) 
        if self.ok:
            self.lineEdit.setText(str(self.text))
        else:
            self.text = ''


#format adapted from PyPi and https://realpython.com/twitter-bot-python-tweepy/

class TwitterStream(tweepy.StreamListener):

    def on_status(self, status):
        #want to return to the user the popular tweets only
        if status.favorite_count is None:
            return
        if not status.retweeted_status:
            return
        

        text = status.text

        #this check is for popularity of the post
        followers = status.user.followers_count
        retweets = status.retweet_count
        favorites = status.favorite_count
        

        #want to make sure the post is recent
        created = status.created_at

        #this info is needed for later data storage
        coords = status.coordinates
        

        #here we will analyze the sentiment of this text post
        blob = TextBlob(text)
            
            
        sent = blob.sentiment
        polarity = sentiment.polarity
        subjectivity = sentiment.subjectivity

        #classify them and store the information somewhere
        self.db = dataset.connect("sqlite:///tweets.db")

        if coords is not None:
            coords = json.dumps(coords)


        self.table = self.db["tweets"]
        self.table.insert(dict(
            coordinates=coords,
            created=created,
            
            user_followers=followers,
            favorite_count=favorites,
            retweet_count=retweets,
            
            text=text,
            sentiment=sent,
            polarity=sent.polarity,
            subjectivity=sent.subjectivity))

        self.processTweets()




    def on_error(self, status_code):
        if status_code == 420:
            return False

    def processTweets(self):
        #this is the parent function which will repeatedly call the 
        #helper that processes each tweet individually
        return
        #case for all target qualities in the posts stored in self.table

            #want to use self.table.distinct('')



        #should most probably call the next Window function from here
        #so that the processes happen sequentially, avoiding user lag



# Annotate the tweet dictionary with any other information we need.
# Store the tweet using a separate database module


def main():

    # remember to UPDATE these keys every day
    auth = tweepy.OAuthHandler('qlAtex8dESsF72L3nvsBxBVZG',
        'P7NSvEQSZTaKu9e6URgqm2ZMCLtAYYWkonRjDDwBM0hjxGTYf8')

    auth.set_access_token('1259937739606294529-D5aURGIWr37Wc7VhBvcUaZ5kCtufCd', 
        'uZeLziNU7nJWMI64ATfnNkVzaeROg1xSGGvjaGzn1FopV')


    api = tweepy.API(auth)

    try: 
        api.verify_credentials()
        print("Authentication OK")
    except:
        print("Error during authentication")

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())

    inpt = SearchWindow.text
    print(inpt)

    
    listener = TwitterStream()
    stream = tweepy.Stream(auth = api.auth, listener = listener)



    #want to also track the top 5 synonyms for this target word

    input_blob = TextBlob(inpt)
    #make sure target word is spelled correctly
    input_blob.correct()

    syns_list = list()
    syns_list.append(inpt)
    for np in input_blob.noun_phrases:
        for syn in np.synsets():
            syns_list.append(syn)


    print(syns_list)
    stream.filter(track = syns_list, languages = ["en"])

 



if __name__ == '__main__':
    main()


