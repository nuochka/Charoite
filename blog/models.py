import datetime
from bson import ObjectId

class Post:
    def __init__(self, title, content, author, image_id=None):
        self.title = title
        self.content = content
        self.author = author
        self.created_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.comments = []
        self.likes = 0
        self.liked_by = []
        self.image_id = image_id

    def to_dict(self):
        return {
            '_id': ObjectId(),
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'created_date': self.created_date,
            'comments': self.comments,
            'likes': self.likes,
            'liked_by': self.liked_by,
            'image_id': self.image_id
        }

class Comment:
    def __init__(self, author, text):
        self._id = ObjectId()
        self.author = author
        self.text = text
        self.created_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def to_dict(self):
        return {
            '_id': ObjectId(),
            'author': self.author,
            'text': self.text,
            'created_date': self.created_date
        }
    
class Notification:
    def __init__(self, from_user, to_user, message, timestamp=None):
        self._id = ObjectId()
        self.from_user = from_user
        self.to_user = to_user
        self.message = message

    def to_dict(self):
        return {
            '_id': self._id,
            'from_user': self.from_user,
            'to_user': self.to_user,
            'message': self.message
        }