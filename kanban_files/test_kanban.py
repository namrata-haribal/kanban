from kanban_files.kanban import app, db
from kanban_files import kanban
import unittest
from flask_login import current_user, login_user, logout_user

class KanbanTests(unittest.TestCase):

    def config_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kanban_test.db'
        self.client = app.test_client()

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kanban_test.db'
        self.client = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def helperAddUser(self):
        # Adding two dummy users.

        user_1 = kanban.User_Data(login_name="name1", login_password=bytes("1_2_3"), salt="rand_string1")
        user_2 = kanban.User_Data(login_name="name2", login_password=bytes("4_5_6"), salt="rand_string2")

        db.session.add(user_1)
        db.session.add(user_2)

        db.session.commit()

    def helperAddTask(self):
        # Adding dummy tasks for both users.

        todo_item_1 = kanban.Kanban_Items(user_id=1, task="to do task", task_status=kanban.TaskStatus.to_do)
        todo_item_2 = kanban.Kanban_Items(user_id=2, task="to do task+", task_status=kanban.TaskStatus.to_do)

        doing_item_1 = kanban.Kanban_Items(user_id=1,task="doing task", task_status=kanban.TaskStatus.doing)
        doing_item_2 = kanban.Kanban_Items(user_id=2, task="doing task+", task_status=kanban.TaskStatus.doing)

        done_item_1 = kanban.Kanban_Items(user_id=1, task="done task", task_status=kanban.TaskStatus.done)
        done_item_2 = kanban.Kanban_Items(user_id=2, task="done task+", task_status=kanban.TaskStatus.done)

        # add all of them.
        db.session.add(todo_item_1)
        db.session.add(todo_item_2)
        db.session.add(doing_item_1)
        db.session.add(doing_item_2)
        db.session.add(done_item_1)
        db.session.add(done_item_2)

        db.session.commit()

    def test_register_pass(self):
        # We will test whether a client registers correctly. This should pass because this username doesn't exist.
        with self.client:
            username = "name12"
            password = "12_22_32"
            response = self.client.post('/register',data=dict(login_name=username,login_password=password), follow_redirects=True)
        return self.assertNotIn(response, kanban.User_Data)

    def test_register_fail(self):
        # We will test whether a client registers correctly. This should fail because this username is taken.
        with self.client:
            username = "name1"
            password = "password"
            response = self.client.post('/register', data=dict(login_name=username,login_password=password), follow_redirects=True)
        return self.assertIn(response, kanban.User_Data)


if __name__=='__main__':
    if __name__ == '__main__':
        unittest.main()



#todo: write tests to register user.
#todo: write tests to log in user.
#todo: write tests to authenticate user.
#todo: write tests to add tasks to kanban_files board.
#todo: write tests to move tasks in the kanban_files board.
