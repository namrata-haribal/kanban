# kanban: The task is to build a simple kanban app using flask.

The kanban app has four pages:

1) The welcome or main page.
2) The sign up page.
3) The login page.
4) The actual Kanban board.

The app begins with the main page, which provides a short description of what the Kanban board does as well as the options to either sign up and create an account or sign in and log into an existing Kanban board.

The sign up options leads to a register page, which prompts the user to enter three items: a username, a password, and the same password a second time to confirm that both passwords match. If the username doesn't already exist in the database, then the user is able to successfully create an account. If not, the register page will reload. Once an attempt to create an account is successfully, the user is redirected to the log in page.

The log in page has a form similar to the one of the user page, except it now only contains a form with two items, a username and a password. Once the user clicks submit after entering their credentials, the app checks against the database whether the username actually exists. If the username exists, then the app proceeds to compare the passwords inputted by the user with the password that is associated with the user that is stored in the app's database.

To make the process as secure as possible, I ensured that when a user is created, a salt of the length of the password inputted is also generated. This salt is then attached to the password provided by the user, and then hashed such that the password is never stored in plain text in our database. When a user attempts to log in, if the app concludes the username inputted from the user in the login form does in fact exist, the salt associated with the user is retrieved, attached to the password inputted by the user, and then hashed. If this hashed value matches the value stored in the database, only then is the user allowed to enter their Kanban board.

Once the user is logged in, they can add tasks in three categories: to do, doing, and done. For each Kanban task, the user can perform two different kinds of actions: 1) Move the task to one of the two other categories & 2) Delete the task. For example, I can log in and input "Submit Kanban assignment" as an item in my to do section of the Kanban board. Then I am able to move this item to either "doing" or "done" sections as well as delete the item altogether. Once the user has finished their work on the app, they can log out, which is an option found at the bottom of the board.

Overall, the flow of the app is envisioned as a complete circle. The user first goes to the main page. They can then register, which takes them to the sign up page. Post signing up, they proceed to the log in page. Likewise, after logging in, they can access their Kanban board. Upon finishing up with the Kanban board, the user is redirected to the main page.


The following tutorials were used for guidance:
1) Building a todo app. https://www.youtube.com/watch?v=4kD-GRF5VPs 
2) Building a login system for Flask: https://www.youtube.com/watch?v=8aTnmsDMldY

